"""
i18n Middleware — foydalanuvchi tiliga qarab xabarlarni tarjima qilish.
"""

import json
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from loguru import logger

from bot.database.repositories import settings_repo
from config import settings


# Til fayllarini yuklash
_translations: Dict[str, Dict[str, str]] = {}
_locales_dir = Path(__file__).parent.parent / "locales"


def load_translations():
    """Barcha til fayllarini yuklaydi."""
    global _translations

    for lang_file in _locales_dir.glob("*.json"):
        lang_code = lang_file.stem  # uz, ru, en
        try:
            with open(lang_file, "r", encoding="utf-8") as f:
                _translations[lang_code] = json.load(f)
            logger.debug(f"Til yuklandi: {lang_code}")
        except Exception as e:
            logger.error(f"Til yuklashda xatolik ({lang_code}): {e}")


def get_text(key: str, lang: str = "uz", **kwargs) -> str:
    """
    Tarjima kaliti bo'yicha matnni qaytaradi.

    Args:
        key: Tarjima kaliti (masalan: 'welcome_message')
        lang: Til kodi ('uz', 'ru', 'en')
        **kwargs: Format o'zgaruvchilari

    Returns:
        str: Tarjima qilingan matn
    """
    if not _translations:
        load_translations()

    lang_data = _translations.get(lang, _translations.get("uz", {}))
    text = lang_data.get(key, key)

    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass

    return text


class LanguageMiddleware(BaseMiddleware):
    """
    Foydalanuvchi tiliga qarab data ga 'lang' va 'get_text' qo'shadi.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Foydalanuvchi ID ni aniqlash
        user_id: Optional[int] = None

        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        # Default til
        lang = settings.DEFAULT_LANGUAGE

        # DB dan foydalanuvchi tilini olish
        if user_id:
            try:
                user_lang = await settings_repo.get_language(user_id)
                if user_lang:
                    lang = user_lang
            except Exception:
                pass

        # Data ga qo'shish
        data["lang"] = lang
        data["_"] = lambda key, **kw: get_text(key, lang, **kw)

        return await handler(event, data)
