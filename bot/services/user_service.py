"""
Foydalanuvchi servisi — ro'yxatdan o'tkazish, ulash, uzish operatsiyalari.
"""

from typing import Optional, Dict, Any
from loguru import logger
from pyrogram import Client as PyrogramClient
from pyrogram.errors import (
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    FloodWait,
)

from bot.database.repositories import user_repo, settings_repo
from config import settings


# Vaqtincha telefon va code saqlash uchun (xotirada)
# {user_id: {"phone": "...", "phone_code_hash": "...", "client": PyrogramClient}}
_pending_connections: Dict[int, Dict[str, Any]] = {}


async def register_user(
    user_id: int,
    first_name: str,
    last_name: Optional[str] = None,
    username: Optional[str] = None,
) -> bool:
    """
    Yangi foydalanuvchini ro'yxatdan o'tkazadi.
    Agar allaqachon mavjud bo'lsa, ma'lumotlarni yangilaydi.

    Args:
        user_id: Telegram user ID
        first_name: Ism
        last_name: Familiya
        username: @username

    Returns:
        bool: Muvaffaqiyatli bo'lsa True
    """
    existing = await user_repo.get_user(user_id)

    if existing:
        # Ma'lumotlarni yangilash
        await user_repo.update_user(
            user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
        )
        await user_repo.update_last_seen(user_id)
        logger.debug(f"Foydalanuvchi yangilandi: {user_id}")
        return True

    # Yangi foydalanuvchi yaratish
    original_name = first_name
    if last_name:
        original_name = f"{first_name} {last_name}"

    success = await user_repo.create_user(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
        original_name=original_name,
    )

    if success:
        # Default sozlamalar yaratish
        await settings_repo.create_default_settings(user_id)
        logger.info(f"Yangi foydalanuvchi ro'yxatdan o'tdi: {user_id}")

    return success


def _cleanup_session_file(user_id: int):
    import os
    from pathlib import Path
    for suffix in [".session", ".session-journal"]:
        session_path = Path(f"data/pending_{user_id}{suffix}")
        if session_path.exists():
            try:
                os.remove(session_path)
                logger.debug(f"Pending session fayl o'chirildi: {session_path}")
            except Exception as e:
                logger.warning(f"Pending session fayl o'chirishda xatolik: {e}")


async def start_connection(user_id: int, phone: str) -> Optional[str]:
    """
    Pyrogram ulanishni boshlaydi — telefon raqamga OTP yuboradi.

    Args:
        user_id: Telegram user ID
        phone: Telefon raqam (masalan: +998901234567)

    Returns:
        str: Muvaffaqiyatli bo'lsa "code_sent", xatolik bo'lsa xatolik xabari
    """
    try:
        # Eski pending sessiyani tozalash (agar mavjud bo'lsa)
        _cleanup_session_file(user_id)
        old_pending = _pending_connections.pop(user_id, None)
        if old_pending:
            try:
                old_client = old_pending.get("client")
                if old_client:
                    await old_client.disconnect()
                    logger.debug(f"Eski pending sessiya tozalandi: {user_id}")
            except Exception:
                pass

        client = PyrogramClient(
            name=f"data/pending_{user_id}",
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            no_updates=True,
        )
        await client.connect()

        sent_code = await client.send_code(phone)

        _pending_connections[user_id] = {
            "phone": phone,
            "phone_code_hash": sent_code.phone_code_hash,
            "client": client,
        }

        logger.info(f"OTP kod yuborildi: {user_id} → {phone}")
        return "code_sent"

    except FloodWait as e:
        logger.warning(f"FloodWait [{user_id}]: {e.value}s")
        return f"⏳ {e.value} soniya kutib turing va qaytadan urinib ko'ring."

    except Exception as e:
        logger.error(f"Ulanish boshlashda xatolik [{user_id}]: {e}")
        _cleanup_session_file(user_id)
        return f"❌ Xatolik: {str(e)}"


async def verify_code(user_id: int, code: str) -> Optional[str]:
    """
    OTP kodni tekshiradi va sessiyani yaratadi.

    Args:
        user_id: Telegram user ID
        code: Foydalanuvchi kiritgan OTP kod

    Returns:
        str: Muvaffaqiyatli bo'lsa "success", xatolik bo'lsa xatolik xabari
    """
    pending = _pending_connections.get(user_id)
    if not pending:
        return "❌ Avval /connect buyrug'ini yuboring va telefon raqamingizni kiriting."

    client: PyrogramClient = pending["client"]
    phone = pending["phone"]
    phone_code_hash = pending["phone_code_hash"]

    try:
        logger.debug(f"sign_in boshlandi: {user_id}, code={code}, hash={phone_code_hash[:8]}...")

        result = await client.sign_in(
            phone_number=phone,
            phone_code_hash=phone_code_hash,
            phone_code=code,
        )

        logger.debug(f"sign_in natijasi: {user_id} -> {type(result)}")

        # Session string olish
        session_string = await client.export_session_string()

        # DB ga saqlash
        await user_repo.save_session(user_id, session_string)
        await user_repo.update_user(user_id, phone=phone)
        await user_repo.set_active(user_id, True)

        # Tozalash
        await client.disconnect()
        _pending_connections.pop(user_id, None)
        _cleanup_session_file(user_id)

        logger.info(f"Foydalanuvchi ulandi: {user_id}")
        return "success"

    except PhoneCodeInvalid:
        logger.warning(f"Noto'g'ri kod: {user_id}")
        return "❌ Kod noto'g'ri! Qaytadan kiriting."

    except PhoneCodeExpired:
        logger.warning(f"Kod expired: {user_id}")
        _pending_connections.pop(user_id, None)
        try:
            await client.disconnect()
        except Exception:
            pass
        _cleanup_session_file(user_id)
        return (
            "❌ Kod muddati tugagan.\n\n"
            "💡 /connect ni qaytadan bosing.\n"
            "⚠️ Muhim: Kodni tez kiriting (30 soniya ichida)!"
        )

    except SessionPasswordNeeded:
        logger.warning(f"2FA parol kerak: {user_id}")
        _pending_connections.pop(user_id, None)
        try:
            await client.disconnect()
        except Exception:
            pass
        _cleanup_session_file(user_id)
        return "❌ Ikki bosqichli parol o'rnatilgan. Hozircha bu qo'llab-quvvatlanmaydi."

    except Exception as e:
        logger.error(f"Kod tekshirishda xatolik [{user_id}]: {type(e).__name__}: {e}")
        _pending_connections.pop(user_id, None)
        try:
            await client.disconnect()
        except Exception:
            pass
        _cleanup_session_file(user_id)
        return f"❌ Xatolik: {str(e)}"


async def disconnect_user(user_id: int) -> bool:
    """
    Foydalanuvchini uzadi — sessiyani o'chiradi va ismni qaytaradi.

    Args:
        user_id: Telegram user ID

    Returns:
        bool: Muvaffaqiyatli bo'lsa True
    """
    try:
        # Ismni asl holatiga qaytarish
        from bot.services.name_service import restore_original_name
        await restore_original_name(user_id)

        # DB da nofaol qilish va sessiyani o'chirish
        await user_repo.set_active(user_id, False)
        await user_repo.update_user(user_id, session_string=None)

        # Pending ni tozalash
        _pending_connections.pop(user_id, None)
        _cleanup_session_file(user_id)

        logger.info(f"Foydalanuvchi uzildi: {user_id}")
        return True

    except Exception as e:
        logger.error(f"Uzishda xatolik [{user_id}]: {e}")
        return False


async def get_user_info(user_id: int) -> Optional[Dict[str, Any]]:
    """Foydalanuvchi to'liq ma'lumotlarini oladi (user + settings)."""
    user = await user_repo.get_user(user_id)
    if not user:
        return None

    user_settings = await settings_repo.get_settings(user_id)
    return {
        "user": user,
        "settings": user_settings,
    }


def is_pending_connection(user_id: int) -> bool:
    """Foydalanuvchi ulanish jarayonida ekanligini tekshiradi."""
    return user_id in _pending_connections


async def cancel_pending_connection(user_id: int):
    """Ulanish jarayonini bekor qiladi va client ni uzadi."""
    pending = _pending_connections.pop(user_id, None)
    if pending:
        try:
            client = pending.get("client")
            if client:
                await client.disconnect()
        except Exception:
            pass
    _cleanup_session_file(user_id)
