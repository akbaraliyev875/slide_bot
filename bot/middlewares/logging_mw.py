"""
Logging Middleware — barcha kiruvchi so'rovlarni loglash.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from loguru import logger


class LoggingMiddleware(BaseMiddleware):
    """Barcha kiruvchi xabar va callback'larni logga yozadi."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user = event.from_user
            logger.info(
                f"[MSG] {user.id} ({user.full_name}): "
                f"{event.text or '[media]'}"
            )
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            logger.info(
                f"[CBQ] {user.id} ({user.full_name}): "
                f"{event.data}"
            )

        return await handler(event, data)
