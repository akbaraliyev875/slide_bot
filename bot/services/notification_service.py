"""
Bildirishnoma servisi — foydalanuvchilarga xabar yuborish.
"""

from typing import Optional
from loguru import logger
from aiogram import Bot


async def send_daily_report(bot: Bot, user_id: int, report_text: str):
    """
    Kunlik hisobot yuboradi.

    Args:
        bot: Aiogram Bot instansiyasi
        user_id: Telegram user ID
        report_text: Hisobot matni
    """
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"📊 <b>Kunlik Hisobot</b>\n\n{report_text}",
            parse_mode="HTML",
        )
        logger.debug(f"Kunlik hisobot yuborildi: {user_id}")
    except Exception as e:
        logger.error(f"Hisobot yuborishda xatolik [{user_id}]: {e}")


async def send_error_alert(
    bot: Bot, user_id: int, error_message: str
):
    """
    Xatolik haqida ogohlantirish yuboradi.

    Args:
        bot: Aiogram Bot instansiyasi
        user_id: Telegram user ID
        error_message: Xatolik xabari
    """
    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"⚠️ <b>Xatolik Yuz Berdi</b>\n\n"
                f"Profil yangilashda muammo:\n"
                f"<code>{error_message}</code>\n\n"
                f"Agar muammo davom etsa, /connect ni qaytadan sinab ko'ring."
            ),
            parse_mode="HTML",
        )
        logger.debug(f"Xatolik ogohlantirildi: {user_id}")
    except Exception as e:
        logger.error(f"Ogohlantirish yuborishda xatolik [{user_id}]: {e}")


async def send_reminder(
    bot: Bot, user_id: int, message: str
):
    """
    Eslatma xabari yuboradi.

    Args:
        bot: Aiogram Bot instansiyasi
        user_id: Telegram user ID
        message: Eslatma matni
    """
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"🔔 <b>Eslatma</b>\n\n{message}",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Eslatma yuborishda xatolik [{user_id}]: {e}")


async def send_session_warning(bot: Bot, user_id: int):
    """Sessiya muddati tugayotgan haqida ogohlantirish."""
    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                "⚠️ <b>Diqqat!</b>\n\n"
                "Sizning sessiyangiz tez orada muddati tugashi mumkin.\n"
                "Iltimos, /connect buyrug'i bilan qaytadan ulaning."
            ),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Sessiya ogohlantirishda xatolik [{user_id}]: {e}")


async def broadcast_message(
    bot: Bot,
    user_ids: list,
    text: str,
    parse_mode: str = "HTML",
) -> dict:
    """
    Bir nechta foydalanuvchilarga xabar yuboradi.

    Args:
        bot: Aiogram Bot instansiyasi
        user_ids: Foydalanuvchilar ID lari ro'yxati
        text: Xabar matni
        parse_mode: Formatlash turi

    Returns:
        dict: {"success": int, "failed": int}
    """
    success = 0
    failed = 0

    for uid in user_ids:
        try:
            await bot.send_message(
                chat_id=uid,
                text=text,
                parse_mode=parse_mode,
            )
            success += 1
        except Exception as e:
            logger.debug(f"Broadcast xatolik [{uid}]: {e}")
            failed += 1

    logger.info(f"Broadcast: {success} muvaffaqiyatli, {failed} xatolik")
    return {"success": success, "failed": failed}
