"""
Yangilanish tarixi repository — update_history jadvali bilan ishlash.
"""

from typing import Optional, List, Dict, Any
from loguru import logger

from bot.database.connection import get_db, close_db


async def add_history(
    user_id: int,
    new_name: str,
    old_name: Optional[str] = None,
    status: str = "success",
    error_message: Optional[str] = None,
) -> bool:
    """Yangilanish tarixiga yozuv qo'shadi."""
    db = await get_db()
    try:
        await db.execute(
            """
            INSERT INTO update_history (user_id, old_name, new_name, status, error_message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, old_name, new_name, status, error_message),
        )
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"Tarix yozishda xatolik: {e}")
        return False
    finally:
        await close_db(db)


async def get_user_history(
    user_id: int, limit: int = 10
) -> List[Dict[str, Any]]:
    """Foydalanuvchining oxirgi yangilanish tarixini oladi."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """
            SELECT * FROM update_history
            WHERE user_id = ?
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await close_db(db)


async def get_today_count(user_id: int) -> int:
    """Bugungi yangilanishlar sonini qaytaradi."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """
            SELECT COUNT(*) as cnt FROM update_history
            WHERE user_id = ? AND DATE(updated_at) = DATE('now')
            """,
            (user_id,),
        )
        row = await cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        await close_db(db)


async def get_total_count(user_id: int) -> int:
    """Jami yangilanishlar sonini qaytaradi."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT COUNT(*) as cnt FROM update_history WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        await close_db(db)


async def get_success_count(user_id: int) -> int:
    """Muvaffaqiyatli yangilanishlar soni."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """
            SELECT COUNT(*) as cnt FROM update_history
            WHERE user_id = ? AND status = 'success'
            """,
            (user_id,),
        )
        row = await cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        await close_db(db)


async def get_failed_count(user_id: int) -> int:
    """Xatolik bilan tugagan yangilanishlar soni."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """
            SELECT COUNT(*) as cnt FROM update_history
            WHERE user_id = ? AND status = 'failed'
            """,
            (user_id,),
        )
        row = await cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        await close_db(db)
