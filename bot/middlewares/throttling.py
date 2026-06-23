"""
Throttling Middleware — Rate limiting (1 daqiqada max 10 ta so'rov).
"""

import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from loguru import logger


class ThrottlingMiddleware(BaseMiddleware):
    """
    Foydalanuvchilardan kelayotgan so'rovlarni cheklaydi.
    Har bir foydalanuvchi uchun 1 daqiqada max 10 ta so'rov ruxsat.
    """

    def __init__(self, rate_limit: int = 10, period: int = 60):
        """
        Args:
            rate_limit: Ruxsat etilgan so'rovlar soni
            period: Vaqt oynasi (soniyalarda)
        """
        super().__init__()
        self.rate_limit = rate_limit
        self.period = period
        # {user_id: [timestamp1, timestamp2, ...]}
        self._requests: Dict[int, list] = {}

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

        user_id = user.id
        now = time.time()

        # Eski so'rovlarni tozalash
        if user_id in self._requests:
            self._requests[user_id] = [
                ts for ts in self._requests[user_id]
                if now - ts < self.period
            ]
        else:
            self._requests[user_id] = []

        # Limit tekshirish
        if len(self._requests[user_id]) >= self.rate_limit:
            logger.warning(f"Throttle: {user_id} limiti oshdi!")
            await event.answer(
                "⏳ Juda ko'p so'rov! Biroz kutib turing...",
            )
            return None

        # So'rovni ro'yxatga qo'shish
        self._requests[user_id].append(now)

        return await handler(event, data)
