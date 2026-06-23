"""
Ban repository — bans jadvali bilan ishlash.
"""

from typing import Optional, List, Dict, Any
from loguru import logger

from bot.database.connection import get_db, close_db


async def ban_user(
    user_id: int, banned_by: int, reason: Optional[str] = None
) -> bool:
    """Foydalanuvchini bloklaydi."""
    db = await get_db()
    try:
        # Bans jadvaliga yozish
        await db.execute(
            """
            INSERT INTO bans (user_id, banned_by, reason)
            VALUES (?, ?, ?)
            """,
            (user_id, banned_by, reason),
        )
        # Users jadvalida is_banned = 1
        await db.execute(
            "UPDATE users SET is_banned = 1, is_active = 0 WHERE id = ?",
            (user_id,),
        )
        await db.commit()
        logger.warning(f"Foydalanuvchi bloklandi: {user_id} (sabab: {reason})")
        return True
    except Exception as e:
        logger.error(f"Bloklashda xatolik: {e}")
        return False
    finally:
        await close_db(db)


async def unban_user(user_id: int) -> bool:
    """Foydalanuvchi blokini ochadi."""
    db = await get_db()
    try:
        # Oxirgi ban yozuvini yangilash
        await db.execute(
            """
            UPDATE bans SET unbanned_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND unbanned_at IS NULL
            """,
            (user_id,),
        )
        # Users jadvalida is_banned = 0
        await db.execute(
            "UPDATE users SET is_banned = 0 WHERE id = ?",
            (user_id,),
        )
        await db.commit()
        logger.info(f"Foydalanuvchi bloki ochildi: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Blok ochishda xatolik: {e}")
        return False
    finally:
        await close_db(db)


async def is_banned(user_id: int) -> bool:
    """Foydalanuvchi bloklangan yoki yo'qligini tekshiradi."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT is_banned FROM users WHERE id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row:
            return bool(row["is_banned"])
        return False
    finally:
        await close_db(db)


async def get_ban_history(user_id: int) -> List[Dict[str, Any]]:
    """Foydalanuvchi ban tarixini oladi."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """
            SELECT * FROM bans
            WHERE user_id = ?
            ORDER BY banned_at DESC
            """,
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await close_db(db)


async def get_all_banned_users() -> List[Dict[str, Any]]:
    """Barcha bloklangan foydalanuvchilarni oladi."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """
            SELECT u.id, u.first_name, u.username, b.reason, b.banned_at
            FROM users u
            JOIN bans b ON u.id = b.user_id
            WHERE u.is_banned = 1 AND b.unbanned_at IS NULL
            ORDER BY b.banned_at DESC
            """
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await close_db(db)
