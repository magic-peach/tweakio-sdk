"""
Unit tests for SQLITE_DB class.
Tests cover database initialization, table creation, and message operations.
"""

import asyncio
import logging
import sqlite3
from unittest.mock import Mock, AsyncMock, patch

import pytest
import aiosqlite

from src.Exceptions.base import StorageError
from src.Interfaces.message_interface import MessageInterface
from src.StorageDB.sqlite_db import SQLITE_DB


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_logger():
    return Mock(spec=logging.Logger)


@pytest.fixture
def mock_queue():
    return asyncio.Queue()


@pytest.fixture
def mock_conn():
    conn = AsyncMock(spec=aiosqlite.Connection)
    conn.execute = AsyncMock()
    conn.executemany = AsyncMock()  # Must be explicitly AsyncMock
    conn.commit = AsyncMock()
    conn.close = AsyncMock()
    return conn


@pytest.fixture
def db_instance(mock_queue, mock_logger):
    return SQLITE_DB(queue=mock_queue, log=mock_logger, db_path=":memory:")


# ============================================================================
# TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_init_db_success(db_instance, mock_conn):
    with patch("aiosqlite.connect", new=AsyncMock(return_value=mock_conn)) as mock_connect:
        await db_instance.init_db()
        mock_connect.assert_called_once_with(":memory:")
        assert db_instance._conn == mock_conn


@pytest.mark.asyncio
async def test_init_db_failure(db_instance):
    with patch("aiosqlite.connect", side_effect=Exception("Connection Failed")):
        with pytest.raises(StorageError, match="Failed to initialize SQLite DB"):
            await db_instance.init_db()


@pytest.mark.asyncio
async def test_create_table_success(db_instance, mock_conn):
    db_instance._conn = mock_conn
    await db_instance.create_table()
    
    # Should execute CREATE TABLE and CREATE INDEX
    assert mock_conn.execute.call_count == 2
    mock_conn.commit.assert_called_once()
    assert "CREATE TABLE" in mock_conn.execute.call_args_list[0][0][0]


@pytest.mark.asyncio
async def test_create_table_no_conn(db_instance):
    with pytest.raises(StorageError, match="Database not initialized"):
        await db_instance.create_table()

@pytest.mark.asyncio
async def test_create_table_failure(db_instance, mock_conn):
    """Test create_table raises StorageError on DB failure."""
    db_instance._conn = mock_conn
    mock_conn.execute.side_effect = Exception("SQL Error")
    
    with pytest.raises(StorageError, match="Failed to create table"):
        await db_instance.create_table()

@pytest.mark.asyncio
async def test_insert_batch_success(db_instance, mock_conn):
    db_instance._conn = mock_conn
    
    # Create valid message mock
    msg = Mock(spec=MessageInterface)
    msg.message_id = "msg123"
    msg.raw_data = "data"
    msg.data_type = "text"
    msg.direction = "in"
    msg.system_hit_time = 100.0
    msg.parent_chat = Mock()
    msg.parent_chat.chatName = "Chat1"
    msg.parent_chat.chatID = "c1"

    await db_instance._insert_batch_internally([msg])

    mock_conn.executemany.assert_called_once()
    mock_conn.commit.assert_called_once()

@pytest.mark.asyncio
async def test_insert_batch_no_conn(db_instance):
    """Test insert_batch raises error if DB not init."""
    with pytest.raises(StorageError, match="Database not initialized"):
        await db_instance._insert_batch_internally([Mock()])


@pytest.mark.asyncio
async def test_check_message_exists_async(db_instance, mock_conn):
    db_instance._conn = mock_conn
    
    # Setup cursor result
    mock_cursor = AsyncMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn.execute.return_value = mock_cursor
    
    exists = await db_instance.check_message_if_exists_async("msg123")
    assert exists is True
    
    # Test not exists
    mock_cursor.fetchone.return_value = None
    exists_false = await db_instance.check_message_if_exists_async("msg999")
    assert exists_false is False


@pytest.mark.asyncio
async def test_enqueue_insert(db_instance):
    msg = Mock(spec=MessageInterface)
    await db_instance.enqueue_insert([msg])
    
    assert db_instance.queue.qsize() == 1
    item = await db_instance.queue.get()
    assert item == msg

@pytest.mark.asyncio
async def test_enqueue_insert_empty(db_instance):
    """Test enqueue_insert with empty list does nothing."""
    await db_instance.enqueue_insert([])
    assert db_instance.queue.empty()


@pytest.mark.asyncio
async def test_start_writer(db_instance):
    """Test start_writer creates a background task."""
    db_instance._writer_loop = AsyncMock()
    await db_instance.start_writer()
    
    assert db_instance._running is True
    assert db_instance._writer_task is not None
    assert not db_instance._writer_task.done()
    
    # Cancel task to cleanup
    db_instance._writer_task.cancel()
    try:
        await db_instance._writer_task
    except asyncio.CancelledError:
        pass

@pytest.mark.asyncio
async def test_start_writer_already_running(db_instance, mock_logger):
    """Test start_writer logs warning if already running."""
    db_instance._writer_task = Mock()
    db_instance._writer_task.done.return_value = False
    
    await db_instance.start_writer()
    mock_logger.warning.assert_called_with("Writer task already running.")

@pytest.mark.asyncio
async def test_close_db(db_instance, mock_conn):
    """Test close_db stops writer and closes connection."""
    db_instance._conn = mock_conn
    db_instance._running = True
    
    # Mock writer task
    async def dummy_writer():
        try:
            while True:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass
            
    db_instance._writer_task = asyncio.create_task(dummy_writer())
    
    await db_instance.close_db()
    
    assert db_instance._running is False
    assert db_instance._writer_task is None
    mock_conn.close.assert_called_once()
    assert db_instance._conn is None

@pytest.mark.asyncio
async def test_context_manager(db_instance):
    """Test context manager calls init and close."""
    db_instance.init_db = AsyncMock()
    db_instance.create_table = AsyncMock()
    db_instance.start_writer = AsyncMock()
    db_instance.close_db = AsyncMock()
    
    async with db_instance as db:
        assert db == db_instance
        
    db_instance.init_db.assert_called_once()
    db_instance.create_table.assert_called_once()
    db_instance.start_writer.assert_called_once()
    db_instance.close_db.assert_called_once()

@pytest.mark.asyncio
async def test_get_all_messages_async(db_instance, mock_conn):
    """Test async get_all_messages."""
    db_instance._conn = mock_conn
    
    mock_cursor = AsyncMock()
    mock_cursor.fetchall.return_value = [{"id": 1, "data": "test"}]
    mock_conn.execute.return_value = mock_cursor
    
    result = await db_instance.get_all_messages_async(limit=5)
    
    assert len(result) == 1
    assert result[0]["data"] == "test"
    mock_conn.execute.assert_called_with(
        "SELECT * FROM messages ORDER BY id DESC LIMIT ? OFFSET ?",
        (5, 0)
    )

@pytest.mark.asyncio
async def test_writer_loop_flush(db_instance):
    """Test writer loop flushes items from queue."""
    db_instance._insert_batch_internally = AsyncMock()
    db_instance.flush_interval = 100 # Long interval, rely on batch size or close
    db_instance.batch_size = 2
    
    msg1 = Mock(spec=MessageInterface)
    msg2 = Mock(spec=MessageInterface)

    # Use side_effect to provide items then stop loop to ensure flush
    # We yield items then raise CancelledError to break loop cleanly BUT
    # Writer cleanup calls flush if batch exists.
    
    async def queue_get_mock():
        if not hasattr(queue_get_mock, "calls"):
            queue_get_mock.calls = 0
        queue_get_mock.calls += 1
        
        if queue_get_mock.calls == 1:
            return msg1
        if queue_get_mock.calls == 2:
            return msg2
        # After 2 items, wait forever to trigger batch flush logic?
        # Or raise CancelledError to exit loop?
        # If we raise CancelledError, loop exits, then "if batch: insert" runs.
        raise asyncio.CancelledError()

    db_instance.queue.get = AsyncMock(side_effect=queue_get_mock)
    
    db_instance._running = True
    try:
        await db_instance._writer_loop()
    except asyncio.CancelledError:
        pass
    
    # Should have flushed at end of loop or during loop
    assert db_instance._insert_batch_internally.called
    args = db_instance._insert_batch_internally.call_args[0][0]
    assert len(args) == 2

@pytest.mark.asyncio
async def test_writer_loop_exception(db_instance, mock_logger):
    """Test writer loop handles exception in queue get."""
    db_instance.flush_interval = 0.01
    db_instance.queue.get = AsyncMock(side_effect=[Exception("Queue Error"), asyncio.CancelledError])
    
    db_instance._running = True
    
    try:
        await asyncio.wait_for(db_instance._writer_loop(), timeout=0.1)
    except (asyncio.TimeoutError, asyncio.CancelledError):
        pass
        
    db_instance._running = False
    
    # Verification: Exception logged
    assert mock_logger.error.called
    assert "Writer loop error" in mock_logger.error.call_args[0][0]

@pytest.mark.asyncio
async def test_insert_batch_internally_exception(db_instance, mock_conn, mock_logger):
    """Test insert batch handles exceptions."""
    db_instance._conn = mock_conn
    msg = Mock(spec=MessageInterface)
    
    # Mock executemany raising error
    mock_conn.executemany.side_effect = Exception("DB Insert Error")
    
    with pytest.raises(StorageError, match="Batch insert failed"):
        await db_instance._insert_batch_internally([msg])
    
    mock_logger.error.assert_called()

@pytest.mark.asyncio
async def test_insert_batch_conversion_error(db_instance, mock_conn, mock_logger):
    """Test skipping messages that fail conversion."""
    db_instance._conn = mock_conn
    
    # Msg causing error
    bad_msg = Mock(spec=MessageInterface)
    type(bad_msg).message_id = property(fget=lambda self: (_ for _ in ()).throw(Exception("Bad Msg")))
    
    await db_instance._insert_batch_internally([bad_msg])
    
    # Should log warning but not raise StorageError if at least one fails but list meant to succeed?
    # Actually code continues.
    mock_logger.warning.assert_called()
    mock_conn.executemany.assert_not_called() # No records

@pytest.mark.asyncio
async def test_check_message_exists_sync(db_instance):
    """Test check_message_exists synchronous."""
    # Mock sqlite3.connect
    mock_sqlite_conn = Mock()
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = (1,)
    mock_sqlite_conn.execute.return_value = mock_cursor
    mock_sqlite_conn.__enter__ = Mock(return_value=mock_sqlite_conn)
    mock_sqlite_conn.__exit__ = Mock(return_value=None)
    
    with patch("sqlite3.connect", return_value=mock_sqlite_conn):
        assert db_instance.check_message_if_exists("msg1") is True
        
        mock_cursor.fetchone.return_value = None
        assert db_instance.check_message_if_exists("msg2") is False

@pytest.mark.asyncio
async def test_get_messages_by_chat(db_instance, mock_conn):
    """Test get_messages_by_chat async."""
    db_instance._conn = mock_conn
    mock_cursor = AsyncMock()
    mock_cursor.fetchall.return_value = [{"id": 1, "data": "chat_msg"}]
    mock_conn.execute.return_value = mock_cursor
    
    rows = await db_instance.get_messages_by_chat("ChatA")
    assert rows[0]["data"] == "chat_msg"

@pytest.mark.asyncio
async def test_get_messages_by_chat_error(db_instance, mock_conn):
    """Test get_messages_by_chat error handling."""
    db_instance._conn = mock_conn
    mock_conn.execute.side_effect = Exception("DB Fail")
    
    rows = await db_instance.get_messages_by_chat("ChatA")
    assert rows == []
