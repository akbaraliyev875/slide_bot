"""
Throttling Middleware — Rate limiting (1 daqiqada max 10 ta so'rov).
"""

import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from loguru import logger


class ThrottlingMiddleware(BaseMiddleware):
    """
    Foydalanuvchilardan kelayotgan so'rovlarni cheklaydi.
    Har bir foydalanuvchi uchun 1 daqiqada max 10 ta so'rov ruxsat.

    FIX:
    - Memory leak tuzatildi: eski foydalanuvchi yozuvlari vaqti-vaqti tozalanadi
    - CallbackQuery ham throttle qilinadi (faqat Message emas)
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
        # Memory leak oldini olish: oxirgi tozalash vaqti
        self._last_cleanup: float = time.time()
        self._cleanup_interval: int = 300  # 5 daqiqada bir tozalash

    def _cleanup_old_entries(self, now: float) -> None:
        """
        Barcha foydalanuvchilar uchun eski yozuvlarni tozalash.
        5 daqiqada bir marta ishlaydi — memory leak oldini oladi.
        """
        if now - self._last_cleanup < self._cleanup_interval:
            return
        self._last_cleanup = now
        empty_keys = []
        for uid, timestamps in self._requests.items():
            fresh = [ts for ts in timestamps if now - ts < self.period]
            if fresh:
                self._requests[uid] = fresh
            else:
                empty_keys.append(uid)
        for uid in empty_keys:
            del self._requests[uid]
        if empty_keys:
            logger.debug(f"Throttling cleanup: {len(empty_keys)} ta eski yozuv o'chirildi")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Faqat Message va CallbackQuery uchun throttle
        if isinstance(event, Message):
            user = event.from_user
            async def send_limit_msg():
                await event.answer("⏳ Juda ko'p so'rov! Biroz kutib turing...")
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            async def send_limit_msg():
                await event.answer("⏳ Juda ko'p so'rov!", show_alert=False)
        else:
            return await handler(event, data)

        if not user:
            return await handler(event, data)

        user_id = user.id
        now = time.time()

        # Global eski yozuvlarni tozalash (memory leak oldini olish)
        self._cleanup_old_entries(now)

        # Bu foydalanuvchi uchun eski so'rovlarni tozalash
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
            await send_limit_msg()
            return None

        # So'rovni ro'yxatga qo'shish
        self._requests[user_id].append(now)

        return await handler(event, data)
