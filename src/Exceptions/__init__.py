"""Tweakio SDK Exceptions Package"""
from src.Exceptions.base import (
    TweakioError,
    ChatError,
    ChatNotFoundError,
    ChatClickError,
    MessageError,
    MessageNotFoundError,
    MessageDataError,
    AuthenticationError,
    QRNotScannedError,
)

__all__ = [
    "TweakioError",
    "ChatError",
    "ChatNotFoundError",
    "ChatClickError",
    "MessageError",
    "MessageNotFoundError",
    "MessageDataError",
    "AuthenticationError",
    "QRNotScannedError",
]
