"""All the Humanized Operation Interface modules"""
from abc import ABC, abstractmethod

from playwright.async_api import Page
import logging

class humanize_operation(ABC):

    @abstractmethod
    def __init__(self, page: Page, log : logging.Logger ) -> None:
        self.page = page
        self.log = log

    @abstractmethod
    async def typing(self, text: str, **kwargs) -> None:
        """This operation ensures the given text is typed on the Web UI with humanized Typing"""
        pass
