"""Message Processor Interface Must be implemented by every Message Processor implementation."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from RepositoryPattern.Interfaces.Chat_Interface import chat_interface
from message_Interface import message_interface
from storage import storage


class message_processor_interface(ABC):
    """
    Message Processor Interface for Messages
    """
    Storage: Optional[storage]

    @abstractmethod
    async def _get_wrapped_Messages(self, retry: int, *args, **kwargs) -> List[message_interface]: pass

    @abstractmethod
    async def Fetcher(self, chat: chat_interface, retry: int, *args, **kwargs) -> List[message_interface]:
        """
        Returns the List of Total messages in that open Chat/Contact.
        Flexibility with batch processing & Safer Filtering approaches.
        """
        pass


2
