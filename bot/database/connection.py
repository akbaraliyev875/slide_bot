"""
SQLite database ulanish moduli — aiosqlite orqali asinxron ishlaydi.
"""

import aiosqlite
from pathlib import Path
from loguru import logger

from config import settings


# Global database yo'li
DB_PATH: Path = settings.db_path


async def get_db() -> aiosqlite.Connection:
    """
    Database ulanishini qaytaradi.
    Har bir chaqiruvda yangi connection ochiladi.
    """
    db = await aiosqlite.connect(str(DB_PATH))
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    """
    Database jadvallarini yaratadi (agar mavjud bo'lmasa).
    Bot ishga tushganda chaqiriladi.
    """
    from bot.database.models import create_tables

    logger.info(f"Database ishga tushirilmoqda: {DB_PATH}")
    await create_tables()
    logger.success("Database muvaffaqiyatli ishga tushirildi!")


async def close_db(db: aiosqlite.Connection):
    """Database ulanishini yopadi."""
    if db:
        await db.close()
