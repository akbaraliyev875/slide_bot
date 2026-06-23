"""
Auth Middleware — bloklangan foydalanuvchilarni tekshirish.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from loguru import logger

from bot.database.repositories import ban_repo


class AuthMiddleware(BaseMiddleware):
    """
    Bloklangan foydalanuvchilarni tekshiradi.
    Agar foydalanuvchi bloklangan bo'lsa, so'rov rad etiladi.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        user = event.from_user
        if not user:
            return await handler(event, data)

        # Bloklangan tekshirish
        if await ban_repo.is_banned(user.id):
            logger.warning(f"Bloklangan foydalanuvchi urinishi: {user.id}")
            await event.answer(
                "⛔ Sizning akkauntingiz bloklangan.\n"
                "Admin bilan bog'laning.",
            )
            return None

        return await handler(event, data)
