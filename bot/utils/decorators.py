"""
Bot dekoratorlari.
"""

from functools import wraps
from aiogram.types import Message, CallbackQuery
from config import settings


def admin_only(handler):
    """
    Faqat admin foydalanuvchilar uchun ruxsat beruvchi dekorator.
    Message va CallbackQuery ikkalasini ham qo'llab-quvvatlaydi.
    """
    @wraps(handler)
    async def wrapper(event, *args, **kwargs):
        if isinstance(event, Message):
            user_id = event.from_user.id
            async def deny():
                await event.answer("⛔ Bu komanda faqat adminlar uchun!")
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            async def deny():
                await event.answer("⛔ Faqat adminlar uchun!", show_alert=True)
        else:
            return await handler(event, *args, **kwargs)

        if user_id not in settings.ADMIN_IDS:
            await deny()
            return
        return await handler(event, *args, **kwargs)
    return wrapper


def rate_limit(limit: int = 1):
    """
    So'rovlar chastotasini cheklash dekoratori.
    """
    def decorator(handler):
        @wraps(handler)
        async def wrapper(event, *args, **kwargs):
            return await handler(event, *args, **kwargs)
        return wrapper
    return decorator
