"""WhatsApp Message Class contracted with Message Interface Template"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Union, Literal, Optional

from playwright.async_api import ElementHandle, Locator

from src.WhatsApp.DefinedClasses.Chat import whatsapp_chat
from src.Interfaces.Message_Interface import message_interface


@dataclass
class whatsapp_message(message_interface):
    Direction: Literal["in", "out"]
    data_id: str

    raw_Data: str
    parent_chat: whatsapp_chat
    MessageUI: Union[ElementHandle, Locator]

    data_type: Optional[str] = None
    MessageID: str = field(init=False)
    System_Hit_Time: float = field(default_factory=time.time)

    def isIncoming(self) -> Optional[bool]:
        """Incoming Status"""
        if not self.Direction: return None
        if self.Direction == "in": return True
        return False

    def __post_init__(self):
        self.MessageID = self._message_key()

    def _message_key(self) -> str:
        return f"wa-msg::{self.data_id}"
