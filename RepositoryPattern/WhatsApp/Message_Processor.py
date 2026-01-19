from __future__ import annotations

from dataclasses import dataclass
from typing import List

from playwright.async_api import Page

import selector_config as sc
from RepositoryPattern.Decorators.Chat_Click_decorator import ensure_chat_clicked
from RepositoryPattern.Interfaces.message_processor_interface import message_processor_interface
from RepositoryPattern.WhatsApp.Chat_Processor import chat_processor
from RepositoryPattern.WhatsApp.DefinedClasses.Chat import whatsapp_chat
from RepositoryPattern.WhatsApp.DefinedClasses.Message import whatsapp_message
from Shared_Resources import logger
from storage import storage


@dataclass
class MessageProcessor(message_processor_interface):

    def __init__(self, Storage: storage, chat_processor: chat_processor, page: Page) -> None:
        self.Storage = Storage
        self.chat_processor = chat_processor
        self.page = page

    @staticmethod
    async def sort_incoming_messages(msgList: List[whatsapp_message]) -> List[whatsapp_message]:
        """Returns incoming messages sorted by direction"""
        if not msgList: raise Exception("Cant Sort incoming messages/ List is Empty/None")
        return [msg for msg in msgList if msg.Direction == "in"]

    @staticmethod
    async def sort_outgoing_messages(msgList: List[whatsapp_message]) -> List[whatsapp_message]:
        """Returns incoming messages sorted by direction"""
        if not msgList: raise Exception("Cant Sort outgoing messages/ List is Empty/None")
        return [msg for msg in msgList if msg.Direction == "out"]

    @ensure_chat_clicked(lambda self, chat: self.chat_processor._click_chat(chat))
    async def _get_wrapped_Messages(self, chat: whatsapp_chat, retry: int = 3, *args, **kwargs) -> List[
        whatsapp_message]:
        wrappedlist: List[whatsapp_message] = []
        try:
            all_Msgs = await sc.messages(page=self.page)
            count = await all_Msgs.count()
            c = 0
            while c < retry and count == 0:
                all_Msgs = await sc.messages(page=self.page)
                count = await all_Msgs.count()
                c += 1

            if not count: raise Exception("Messages Not Found from UI / get wrapped messages / WA ")

            for i in range(count):
                msg = all_Msgs.nth(i)
                text = await sc.get_message_text(msg)
                data_id = await sc.get_dataID(msg)

                c2 = 0
                while not data_id and c2 < 3:
                    data_id = await sc.get_dataID(msg)
                    c2 += 1

                if not data_id:
                    logger.error("Data ID in WA / get wrapped Messages , None/Empty. Skipping")
                    continue

                wrappedlist.append(
                    whatsapp_message(
                        MessageUI=msg,
                        Direction="in" if await msg.locator(".message-in").count() > 0 else "out",
                        raw_Data=text,
                        parent_chat=chat,
                        data_id=data_id
                        # Todo , Adding proper Type Checking Message. [txt , ing , vid, quoted]
                    )
                )
        except Exception as e:
            logger.error(f"WA / [MessageProcessor] {e}", exc_info=True)
        return wrappedlist

    async def Fetcher(self, chat: whatsapp_chat, retry : int , *args, **kwargs) -> List[whatsapp_message]:
        msgList : List[whatsapp_message] = await self._get_wrapped_Messages(chat, *args, **kwargs)
        try :
            # Todo , Fix the Storage Enqueue to take the Interface based Serialized Object and add in DB
            await self.Storage.enqueue_insert(msgList)
        except Exception as e:
            logger.error(f"WA / [MessageProcessor] / Fetcher {e}", exc_info=True)
        return msgList
