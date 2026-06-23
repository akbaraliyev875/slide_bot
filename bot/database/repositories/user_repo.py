"""
Foydalanuvchi repository — users jadvali bilan ishlash.
"""

from typing import Optional, List, Dict, Any
from loguru import logger

from bot.database.connection import get_db, close_db


async def create_user(
    user_id: int,
    first_name: str,
    last_name: Optional[str] = None,
    username: Optional[str] = None,
    original_name: Optional[str] = None,
) -> bool:
    """Yangi foydalanuvchi yaratadi."""
    if original_name is None:
        original_name = first_name
        if last_name:
            original_name = f"{first_name} {last_name}"

    db = await get_db()
    try:
        await db.execute(
            """
            INSERT OR IGNORE INTO users (id, username, first_name, last_name, original_name)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, username, first_name, last_name, original_name),
        )
        await db.commit()
        logger.info(f"Foydalanuvchi yaratildi: {user_id} ({first_name})")
        return True
    except Exception as e:
        logger.error(f"Foydalanuvchi yaratishda xatolik: {e}")
        return False
    finally:
        await close_db(db)


async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Foydalanuvchini ID bo'yicha oladi."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        await close_db(db)


async def update_user(user_id: int, **kwargs) -> bool:
    """Foydalanuvchi ma'lumotlarini yangilaydi."""
    if not kwargs:
        return False

    fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values())
    values.append(user_id)

    db = await get_db()
    try:
        await db.execute(
            f"UPDATE users SET {fields}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            values,
        )
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"Foydalanuvchi yangilashda xatolik: {e}")
        return False
    finally:
        await close_db(db)


async def get_all_active_users() -> List[Dict[str, Any]]:
    """Barcha aktiv foydalanuvchilarni oladi."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM users WHERE is_active = 1 AND is_banned = 0"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await close_db(db)


async def get_all_users() -> List[Dict[str, Any]]:
    """Barcha foydalanuvchilarni oladi."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await close_db(db)


async def get_users_count() -> Dict[str, int]:
    """Foydalanuvchilar statistikasi."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT COUNT(*) as total FROM users")
        total = (await cursor.fetchone())["total"]

        cursor = await db.execute(
            "SELECT COUNT(*) as active FROM users WHERE is_active = 1"
        )
        active = (await cursor.fetchone())["active"]

        cursor = await db.execute(
            "SELECT COUNT(*) as banned FROM users WHERE is_banned = 1"
        )
        banned = (await cursor.fetchone())["banned"]

        return {"total": total, "active": active, "banned": banned}
    finally:
        await close_db(db)


async def set_active(user_id: int, is_active: bool) -> bool:
    """Foydalanuvchini aktiv/nofaol qiladi."""
    return await update_user(user_id, is_active=int(is_active))


async def set_banned(user_id: int, is_banned: bool) -> bool:
    """Foydalanuvchini bloklash/ochish."""
    return await update_user(user_id, is_banned=int(is_banned))


async def update_last_seen(user_id: int) -> bool:
    """Oxirgi ko'rilgan vaqtni yangilaydi."""
    db = await get_db()
    try:
        await db.execute(
            "UPDATE users SET last_seen = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,),
        )
        await db.commit()
        return True
    finally:
        await close_db(db)


async def save_session(user_id: int, session_string: str) -> bool:
    """Pyrogram sessiya string ni saqlaydi."""
    return await update_user(user_id, session_string=session_string)


async def get_session(user_id: int) -> Optional[str]:
    """Pyrogram sessiya string ni oladi."""
    user = await get_user(user_id)
    if user:
        return user.get("session_string")
    return None
