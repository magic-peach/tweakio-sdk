"""
WhatsApp Chat contracted with ChatInterface Template
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional, Union

from playwright.async_api import ElementHandle, Locator

from src.Interfaces.Chat_Interface import chat_interface


@dataclass
class whatsapp_chat(chat_interface):
    """WhatsApp wrapped Chat Object"""

    chatName: str
    chatUI: Optional[Union[ElementHandle, Locator]]
    chatID: str = field(init=False)
    System_Hit_Time: float = field(default_factory=time.time)

    def __post_init__(self):
        self.chatID = self._chat_key()

    def _chat_key(self) -> str:
        return f"wa::{self.chatName.lower().strip()}"
