"""
Dekoratorlar — admin_only va boshqa tekshirish dekoratorlari.
"""

from functools import wraps
from aiogram.types import Message

from config import settings


def admin_only(handler):
    """
    Faqat adminlar uchun dekorator.
    Agar foydalanuvchi admin bo'lmasa, xabar yuboriladi.
    """
    @wraps(handler)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id not in settings.ADMIN_IDS:
            await message.answer(
                "⛔ Bu komanda faqat adminlar uchun!"
            )
            return
        return await handler(message, *args, **kwargs)
    return wrapper
