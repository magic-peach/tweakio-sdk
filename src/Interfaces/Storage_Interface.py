"""Storage Interface"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict

from src.Interfaces.Message_Interface import message_interface


class StorageInterface(ABC):
    """Storage Interface"""

    def __init__(self, queue: asyncio.Queue, log : logging.Logger):
        """This Queue is Explicitly given to work as a Global Enqueue."""
        self.queue = queue
        self.log = log

    @abstractmethod
    def init_db(self): pass

    @abstractmethod
    def create_table(self): pass

    @abstractmethod
    def start_writer(self): pass

    @abstractmethod
    async def enqueue_insert(self, msgs: List[message_interface]): pass

    @abstractmethod
    async def _insert_batch_internally(self, msgs: List[message_interface]): pass

    @abstractmethod
    def check_message_if_exists(self, msg_id: str) -> bool: pass

    @abstractmethod
    def get_all_messages(self) -> List[Dict]: pass

    @abstractmethod
    async def close_db(self): pass
