"""
Foydalanuvchi handler'lari — asosiy buyruqlar.
/start, /connect, /disconnect, /status, /stats, /history, /uptime, /help, /session, /feedback
"""

from aiogram import Router, F
from aiogram.types import Message, ContentType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from bot.services import user_service
from bot.services.scheduler_service import (
    add_user_job,
    remove_user_job,
    get_job_next_run,
    get_active_jobs_count,
    get_bot_start_time,
)
from bot.database.repositories import (
    user_repo,
    settings_repo,
    history_repo,
)
from bot.keyboards.inline import get_main_menu_keyboard
from bot.keyboards.reply import (
    get_phone_keyboard,
    get_cancel_keyboard,
    remove_keyboard,
)
from bot.utils.time_utils import format_next_update, get_uptime
from bot.middlewares.i18n import get_text
from config import settings


# Router yaratish
router = Router(name="user")


# ——— FSM States ———
class ConnectStates(StatesGroup):
    waiting_phone = State()
    waiting_code = State()


class FeedbackStates(StatesGroup):
    waiting_message = State()


# ——— /start ———
@router.message(Command("start"))
async def cmd_start(message: Message, lang: str = "uz", **kwargs):
    """Botni ishga tushirish va foydalanuvchini ro'yxatdan o'tkazish."""
    user = message.from_user

    # Ro'yxatdan o'tkazish
    await user_service.register_user(
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
    )

    # Xush kelibsiz xabari
    text = get_text("welcome_message", lang, name=user.first_name)
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(),
    )


# ——— /help ———
@router.message(Command("help"))
async def cmd_help(message: Message, lang: str = "uz", **kwargs):
    """Barcha buyruqlar ro'yxati."""
    text = get_text("help_message", lang)
    await message.answer(text, parse_mode="HTML")


# ——— /connect ———
@router.message(Command("connect"))
async def cmd_connect(message: Message, state: FSMContext, lang: str = "uz", **kwargs):
    """Profilni ulash — telefon raqam so'rash."""
    user_id = message.from_user.id

    # Allaqachon ulangan tekshirish
    user = await user_repo.get_user(user_id)
    if user and user.get("is_active"):
        await message.answer(get_text("already_connected", lang))
        return

    # API_ID va API_HASH tekshirish
    if not settings.API_ID or not settings.API_HASH:
        await message.answer(
            "❌ Bot sozlanmagan. Admin bilan bog'laning.\n"
            "(API_ID va API_HASH .env faylda yo'q)"
        )
        return

    await message.answer(
        get_text("connect_phone", lang),
        reply_markup=get_phone_keyboard(),
    )
    await state.set_state(ConnectStates.waiting_phone)


# ——— Telefon raqam qabul qilish ———
@router.message(ConnectStates.waiting_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext, lang: str = "uz", **kwargs):
    """Kontakt orqali telefon raqamni qabul qilish."""
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = f"+{phone}"

    await _process_phone(message, state, phone, lang)


@router.message(ConnectStates.waiting_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext, lang: str = "uz", **kwargs):
    """Matn orqali telefon raqamni qabul qilish."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            get_text("cancel", lang),
            reply_markup=remove_keyboard(),
        )
        return

    phone = message.text.strip()
    if not phone.startswith("+"):
        phone = f"+{phone}"

    await _process_phone(message, state, phone, lang)


async def _process_phone(message: Message, state: FSMContext, phone: str, lang: str):
    """Telefon raqamni qayta ishlash."""
    user_id = message.from_user.id

    await message.answer(
        "⏳ Kod yuborilmoqda...",
        reply_markup=remove_keyboard(),
    )

    result = await user_service.start_connection(user_id, phone)

    if result == "code_sent":
        await message.answer(
            get_text("connect_code", lang),
            parse_mode="HTML",
            reply_markup=get_cancel_keyboard(),
        )
        await state.set_state(ConnectStates.waiting_code)
    else:
        await message.answer(result, reply_markup=remove_keyboard())
        await state.clear()


# ——— OTP kod qabul qilish ———
@router.message(ConnectStates.waiting_code, F.text)
async def process_code(message: Message, state: FSMContext, lang: str = "uz", **kwargs):
    """OTP kodni tekshirish."""
    if message.text == "❌ Bekor qilish":
        await user_service.cancel_pending_connection(message.from_user.id)
        await state.clear()
        await message.answer(
            get_text("cancel", lang),
            reply_markup=remove_keyboard(),
        )
        return

    import re
    code = re.sub(r"\D", "", message.text)
    user_id = message.from_user.id

    await message.answer("⏳ Tekshirilmoqda...")

    result = await user_service.verify_code(user_id, code)

    if result == "success":
        # Scheduler job qo'shish
        user_settings = await settings_repo.get_settings(user_id)
        interval = 60
        if user_settings:
            interval = user_settings.get("update_interval", 60)

        await add_user_job(user_id, interval)

        text = get_text("connect_success", lang, interval=interval)
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=remove_keyboard(),
        )
    else:
        await message.answer(result, reply_markup=get_cancel_keyboard())
        return  # State ni o'zgartirmaslik — qaytadan urinish mumkin

    await state.clear()


# ——— /disconnect ———
@router.message(Command("disconnect"))
async def cmd_disconnect(message: Message, lang: str = "uz", **kwargs):
    """Profilni uzish."""
    user_id = message.from_user.id

    user = await user_repo.get_user(user_id)
    if not user or not user.get("is_active"):
        await message.answer(get_text("not_connected", lang))
        return

    # Scheduler job o'chirish
    await remove_user_job(user_id)

    # Profilni uzish
    success = await user_service.disconnect_user(user_id)

    if success:
        await message.answer(get_text("disconnect_success", lang))
    else:
        await message.answer(get_text("disconnect_error", lang))


# ——— /status ———
@router.message(Command("status"))
async def cmd_status(message: Message, lang: str = "uz", **kwargs):
    """Bot holatini ko'rsatish."""
    user_id = message.from_user.id
    user = await user_repo.get_user(user_id)

    if not user or not user.get("is_active"):
        await message.answer(
            get_text("status_inactive", lang),
            parse_mode="HTML",
        )
        return

    user_settings = await settings_repo.get_settings(user_id)
    interval = user_settings.get("update_interval", 60) if user_settings else 60
    timezone = user_settings.get("timezone", "Asia/Tashkent") if user_settings else "Asia/Tashkent"
    total = await history_repo.get_total_count(user_id)
    next_update = format_next_update(interval, timezone)

    text = get_text(
        "status_active", lang,
        next_update=next_update,
        total_updates=total,
        interval=interval,
    )
    await message.answer(text, parse_mode="HTML")


# ——— /stats ———
@router.message(Command("stats"))
async def cmd_stats(message: Message, lang: str = "uz", **kwargs):
    """Shaxsiy statistika."""
    user_id = message.from_user.id

    total = await history_repo.get_total_count(user_id)
    today = await history_repo.get_today_count(user_id)
    success = await history_repo.get_success_count(user_id)
    failed = await history_repo.get_failed_count(user_id)

    user = await user_repo.get_user(user_id)
    registered = user.get("created_at", "—") if user else "—"

    text = get_text(
        "stats_message", lang,
        total=total,
        today=today,
        success=success,
        failed=failed,
        registered=registered,
    )
    await message.answer(text, parse_mode="HTML")


# ——— /history ———
@router.message(Command("history"))
async def cmd_history(message: Message, lang: str = "uz", **kwargs):
    """Oxirgi 10 ta yangilanish tarixi."""
    user_id = message.from_user.id
    history = await history_repo.get_user_history(user_id, limit=10)

    if not history:
        await message.answer(get_text("history_empty", lang))
        return

    lines = []
    for i, h in enumerate(history, 1):
        status_icon = "✅" if h["status"] == "success" else "❌"
        lines.append(
            f"{i}. {status_icon} <code>{h['new_name']}</code> — {h['updated_at']}"
        )

    history_text = "\n".join(lines)
    text = get_text(
        "history_message", lang,
        count=len(history),
        history=history_text,
    )
    await message.answer(text, parse_mode="HTML")


# ——— /uptime ———
@router.message(Command("uptime"))
async def cmd_uptime(message: Message, lang: str = "uz", **kwargs):
    """Bot ishlash vaqti."""
    start_time = get_bot_start_time()
    if start_time:
        uptime_str = get_uptime(start_time)
    else:
        uptime_str = "N/A"

    jobs = get_active_jobs_count()

    text = get_text(
        "uptime_message", lang,
        uptime=uptime_str,
        jobs=jobs,
    )
    await message.answer(text, parse_mode="HTML")


# ——— /session ———
@router.message(Command("session"))
async def cmd_session(message: Message, lang: str = "uz", **kwargs):
    """Sessiya ma'lumotlari."""
    user_id = message.from_user.id
    user = await user_repo.get_user(user_id)

    if not user:
        await message.answer(get_text("not_connected", lang))
        return

    phone = user.get("phone", "—")
    status = "✅ Aktiv" if user.get("is_active") else "❌ Nofaol"
    connected_at = user.get("updated_at", "—")

    text = get_text(
        "session_info", lang,
        phone=phone,
        status=status,
        connected_at=connected_at,
    )
    await message.answer(text, parse_mode="HTML")


# ——— /feedback ———
@router.message(Command("feedback"))
async def cmd_feedback(message: Message, state: FSMContext, lang: str = "uz", **kwargs):
    """Taklif/muammo xabari."""
    await message.answer(
        get_text("feedback_prompt", lang),
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(FeedbackStates.waiting_message)


@router.message(FeedbackStates.waiting_message, F.text)
async def process_feedback(message: Message, state: FSMContext, lang: str = "uz", **kwargs):
    """Feedback xabarini qayta ishlash."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            get_text("cancel", lang),
            reply_markup=remove_keyboard(),
        )
        return

    user = message.from_user

    # Admin larga yuborish
    feedback_text = get_text(
        "feedback_received", lang,
        name=user.full_name,
        user_id=user.id,
        message=message.text,
    )

    for admin_id in settings.ADMIN_IDS:
        try:
            await message.bot.send_message(
                chat_id=admin_id,
                text=feedback_text,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Admin ga feedback yuborishda xatolik [{admin_id}]: {e}")

    await message.answer(
        get_text("feedback_sent", lang),
        reply_markup=remove_keyboard(),
    )
    await state.clear()
