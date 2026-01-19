"""WhatsApp Message Class contracted with Message Interface Template"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Union, Literal

from playwright.async_api import ElementHandle, Locator

from RepositoryPattern.Interfaces.message_Interface import message_interface
from Chat import whatsapp_chat


@dataclass
class whatsapp_message(message_interface):
    """WhatsApp Message Class contracted with Message Interface Template"""
    Direction : Literal["in", "out"]
    data_id : str

    System_Hit_Time: float = field(default_factory=time.time)
    raw_Data: str
    data_type: str
    parent_chat: whatsapp_chat
    MessageID: str
    MessageUI: Union[ElementHandle, Locator]

    def __post_init__(self):
        self.MessageID = self._message_key(self)

    @staticmethod
    def _message_key(message: whatsapp_message) -> str:
        return str(id(message))
