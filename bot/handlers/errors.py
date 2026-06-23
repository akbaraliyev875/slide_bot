"""
Xatoliklarni ushlash handler'i — global error handler.
"""

from aiogram import Router
from aiogram.types import ErrorEvent
from loguru import logger

from bot.database.connection import get_db, close_db


# Router yaratish
router = Router(name="errors")


@router.error()
async def error_handler(event: ErrorEvent):
    """
    Barcha kutilmagan xatoliklarni ushlaydi va logga yozadi.
    """
    exception = event.exception
    update = event.update

    logger.error(
        f"Xatolik yuz berdi: {type(exception).__name__}: {exception}"
    )

    # Xatolikni DB ga ham yozish
    try:
        db = await get_db()
        await db.execute(
            """
            INSERT INTO system_logs (level, message, user_id)
            VALUES (?, ?, ?)
            """,
            (
                "ERROR",
                f"{type(exception).__name__}: {str(exception)}",
                None,
            ),
        )
        await db.commit()
        await close_db(db)
    except Exception as db_err:
        logger.error(f"DB ga xatolik yozishda muammo: {db_err}")

    # Foydalanuvchiga xabar yuborish
    try:
        if update and update.message:
            await update.message.answer(
                "❌ Kutilmagan xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring."
            )
        elif update and update.callback_query:
            await update.callback_query.answer(
                "❌ Xatolik yuz berdi!", show_alert=True
            )
    except Exception:
        pass
