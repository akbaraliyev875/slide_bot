"""
Nom yangilash servisi — asosiy biznes mantiq.
Foydalanuvchi profil ismini vaqt bilan yangilaydi.
"""

from typing import Optional
from loguru import logger
from pyrogram import Client as PyrogramClient
from pyrogram.errors import (
    FloodWait,
    UserDeactivated,
    AuthKeyUnregistered,
    SessionRevoked,
)

from bot.database.repositories import user_repo, settings_repo, history_repo
from bot.utils.time_utils import get_current_time, format_time
from bot.utils.name_utils import strip_time_tag, add_time_tag, validate_name_length
from config import settings


async def update_user_name(user_id: int) -> bool:
    """
    Foydalanuvchi profil ismini joriy vaqt bilan yangilaydi.

    Jarayon:
    1. DB dan foydalanuvchi va sozlamalar olish
    2. Joriy vaqtni timezone bo'yicha hisoblash
    3. Vaqt formatini settings bo'yicha formatlash
    4. Eski vaqt tegini regex bilan o'chirish
    5. Yangi ism yaratish: {original_name} {prefix} [{time}]
    6. Pyrogram orqali profil yangilash
    7. Natijani tarixga yozish

    Args:
        user_id: Telegram foydalanuvchi ID si

    Returns:
        bool: Muvaffaqiyatli yangilangan bo'lsa True
    """
    try:
        # 1. Foydalanuvchi ma'lumotlari
        user = await user_repo.get_user(user_id)
        if not user:
            logger.warning(f"Foydalanuvchi topilmadi: {user_id}")
            return False

        if not user.get("is_active"):
            logger.debug(f"Foydalanuvchi aktiv emas: {user_id}")
            return False

        # Session string tekshirish
        session_string = user.get("session_string")
        if not session_string:
            logger.warning(f"Session string yo'q: {user_id}")
            return False

        # 2. Sozlamalar
        user_settings = await settings_repo.get_settings(user_id)
        if not user_settings:
            logger.warning(f"Sozlamalar topilmadi: {user_id}")
            return False

        timezone = user_settings.get("timezone", "Asia/Tashkent")
        time_format = user_settings.get("time_format", "HH:MM")
        bracket_style = user_settings.get("bracket_style", "[]")
        prefix_text = user_settings.get("prefix_text", "")

        # 3. Joriy vaqtni hisoblash
        current_time = get_current_time(timezone)
        time_str = format_time(current_time, time_format)

        # 4. Asl ismni olish
        original_name = user.get("original_name", user.get("first_name", ""))

        # 5. Yangi ism yaratish
        new_name = add_time_tag(original_name, time_str, bracket_style, prefix_text)

        # Uzunlik tekshirish
        if not validate_name_length(new_name):
            error_msg = f"Ism juda uzun: {len(new_name)} belgi (max 64)"
            logger.warning(f"{error_msg}: {user_id}")
            await history_repo.add_history(
                user_id=user_id,
                new_name=new_name,
                old_name=original_name,
                status="failed",
                error_message=error_msg,
            )
            return False

        # 6. Pyrogram orqali profil yangilash
        old_name = strip_time_tag(original_name)
        success = await _update_profile_via_pyrogram(
            user_id, session_string, new_name
        )

        if success:
            # 7. Tarixga yozish
            await history_repo.add_history(
                user_id=user_id,
                new_name=new_name,
                old_name=old_name,
                status="success",
            )
            logger.info(f"Ism yangilandi: {user_id} → {new_name}")
            return True
        else:
            return False

    except Exception as e:
        logger.error(f"Nom yangilashda xatolik [{user_id}]: {e}")
        await history_repo.add_history(
            user_id=user_id,
            new_name="",
            old_name="",
            status="failed",
            error_message=str(e),
        )
        return False


async def _update_profile_via_pyrogram(
    user_id: int, session_string: str, new_name: str
) -> bool:
    """
    Pyrogram orqali foydalanuvchi profilini yangilaydi.

    Args:
        user_id: Telegram ID
        session_string: Pyrogram session string
        new_name: Yangi profil ismi

    Returns:
        bool: Muvaffaqiyatli bo'lsa True
    """
    try:
        # Ismni first_name va last_name ga ajratish
        name_parts = new_name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        async with PyrogramClient(
            name=f"user_{user_id}",
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            session_string=session_string,
            in_memory=True,
            no_updates=True,
        ) as app:
            await app.update_profile(
                first_name=first_name,
                last_name=last_name,
            )
            return True

    except FloodWait as e:
        logger.warning(
            f"FloodWait: {e.value} soniya kutish kerak [{user_id}]"
        )
        await history_repo.add_history(
            user_id=user_id,
            new_name=new_name,
            status="failed",
            error_message=f"FloodWait: {e.value}s",
        )
        return False

    except (UserDeactivated, AuthKeyUnregistered, SessionRevoked) as e:
        logger.error(f"Sessiya muammosi [{user_id}]: {e}")
        # Foydalanuvchini nofaol qilish
        await user_repo.set_active(user_id, False)
        await history_repo.add_history(
            user_id=user_id,
            new_name=new_name,
            status="failed",
            error_message=f"Session error: {type(e).__name__}",
        )
        return False

    except Exception as e:
        logger.error(f"Profil yangilashda xatolik [{user_id}]: {e}")
        await history_repo.add_history(
            user_id=user_id,
            new_name=new_name,
            status="failed",
            error_message=str(e),
        )
        return False


async def restore_original_name(user_id: int) -> bool:
    """
    Foydalanuvchi ismini asl holatiga qaytaradi.

    Args:
        user_id: Telegram foydalanuvchi ID

    Returns:
        bool: Muvaffaqiyatli qaytarilsa True
    """
    try:
        user = await user_repo.get_user(user_id)
        if not user:
            return False

        session_string = user.get("session_string")
        original_name = user.get("original_name", user.get("first_name", ""))

        if session_string:
            return await _update_profile_via_pyrogram(
                user_id, session_string, original_name
            )
        return False

    except Exception as e:
        logger.error(f"Ism qaytarishda xatolik [{user_id}]: {e}")
        return False
