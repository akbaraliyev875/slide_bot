"""
Sozlamalar repository — user_settings jadvali bilan ishlash.
"""

from typing import Optional, Dict, Any
from loguru import logger

from bot.database.connection import get_db, close_db
from config import settings as app_settings


async def create_default_settings(user_id: int) -> bool:
    """Foydalanuvchi uchun default sozlamalar yaratadi."""
    db = await get_db()
    try:
        await db.execute(
            """
            INSERT OR IGNORE INTO user_settings (user_id, timezone, language, update_interval)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                app_settings.DEFAULT_TIMEZONE,
                app_settings.DEFAULT_LANGUAGE,
                app_settings.DEFAULT_INTERVAL,
            ),
        )
        await db.commit()
        logger.info(f"Default sozlamalar yaratildi: user_id={user_id}")
        return True
    except Exception as e:
        logger.error(f"Sozlamalar yaratishda xatolik: {e}")
        return False
    finally:
        await close_db(db)


async def get_settings(user_id: int) -> Optional[Dict[str, Any]]:
    """Foydalanuvchi sozlamalarini oladi."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM user_settings WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        await close_db(db)


async def update_settings(user_id: int, **kwargs) -> bool:
    """Foydalanuvchi sozlamalarini yangilaydi."""
    if not kwargs:
        return False

    fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values())
    values.append(user_id)

    db = await get_db()
    try:
        await db.execute(
            f"UPDATE user_settings SET {fields} WHERE user_id = ?",
            values,
        )
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"Sozlamalar yangilashda xatolik: {e}")
        return False
    finally:
        await close_db(db)


async def get_timezone(user_id: int) -> str:
    """Foydalanuvchi timezone ni oladi."""
    s = await get_settings(user_id)
    if s:
        return s.get("timezone", app_settings.DEFAULT_TIMEZONE)
    return app_settings.DEFAULT_TIMEZONE


async def get_language(user_id: int) -> str:
    """Foydalanuvchi tilini oladi."""
    s = await get_settings(user_id)
    if s:
        return s.get("language", app_settings.DEFAULT_LANGUAGE)
    return app_settings.DEFAULT_LANGUAGE
