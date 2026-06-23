"""
Sozlamalar handler'lari — settings, timezone, format, interval, prefix, notify, language.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.database.repositories import settings_repo
from bot.keyboards.inline import (
    get_settings_keyboard,
    get_timezone_keyboard,
    get_format_keyboard,
    get_bracket_keyboard,
    get_interval_keyboard,
    get_language_keyboard,
    get_notify_keyboard,
)
from bot.keyboards.reply import get_cancel_keyboard, remove_keyboard
from bot.utils.validators import validate_prefix, validate_timezone
from bot.middlewares.i18n import get_text


# Router yaratish
router = Router(name="settings")


# FSM States
class PrefixStates(StatesGroup):
    waiting_prefix = State()


# ——— /settings ———
@router.message(Command("settings"))
async def cmd_settings(message: Message, lang: str = "uz", **kwargs):
    """Sozlamalar menyusi."""
    text = get_text("settings_menu", lang)
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(),
    )


# ——— /timezone ———
@router.message(Command("timezone"))
async def cmd_timezone(message: Message, **kwargs):
    """Vaqt mintaqasini tanlash."""
    await message.answer(
        "🕐 <b>Vaqt mintaqasini tanlang:</b>",
        parse_mode="HTML",
        reply_markup=get_timezone_keyboard(),
    )


# ——— /format ———
@router.message(Command("format"))
async def cmd_format(message: Message, **kwargs):
    """Vaqt formatini tanlash."""
    await message.answer(
        "📝 <b>Vaqt formatini tanlang:</b>",
        parse_mode="HTML",
        reply_markup=get_format_keyboard(),
    )


# ——— /interval ———
@router.message(Command("interval"))
async def cmd_interval(message: Message, **kwargs):
    """Yangilanish intervalini tanlash."""
    await message.answer(
        "⏱ <b>Yangilanish intervalini tanlang:</b>",
        parse_mode="HTML",
        reply_markup=get_interval_keyboard(),
    )


# ——— /prefix ———
@router.message(Command("prefix"))
async def cmd_prefix(message: Message, state: FSMContext, lang: str = "uz", **kwargs):
    """Prefix matn o'rnatish."""
    await message.answer(
        get_text("prefix_prompt", lang),
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(PrefixStates.waiting_prefix)


@router.message(PrefixStates.waiting_prefix, F.text)
async def process_prefix(message: Message, state: FSMContext, lang: str = "uz", **kwargs):
    """Prefix matnni qabul qilish."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            get_text("cancel", lang),
            reply_markup=remove_keyboard(),
        )
        return

    prefix = message.text.strip()
    user_id = message.from_user.id

    # Bo'sh xabar — prefikni o'chirish
    if not prefix:
        await settings_repo.update_settings(user_id, prefix_text="")
        await message.answer(
            get_text("prefix_cleared", lang),
            reply_markup=remove_keyboard(),
        )
        await state.clear()
        return

    # Validatsiya
    if not validate_prefix(prefix):
        await message.answer("❌ Prefix juda uzun! Maksimal 20 belgi.")
        return

    await settings_repo.update_settings(user_id, prefix_text=prefix)
    await message.answer(
        get_text("prefix_changed", lang, prefix=prefix),
        parse_mode="HTML",
        reply_markup=remove_keyboard(),
    )
    await state.clear()


# ——— /notify ———
@router.message(Command("notify"))
async def cmd_notify(message: Message, **kwargs):
    """Bildirishnoma sozlamalari."""
    user_id = message.from_user.id
    user_settings = await settings_repo.get_settings(user_id)

    notify_daily = bool(user_settings.get("notify_daily", 0)) if user_settings else False
    notify_errors = bool(user_settings.get("notify_errors", 1)) if user_settings else True

    await message.answer(
        "🔔 <b>Bildirishnoma sozlamalari:</b>",
        parse_mode="HTML",
        reply_markup=get_notify_keyboard(notify_daily, notify_errors),
    )


# ——— /language ———
@router.message(Command("language"))
async def cmd_language(message: Message, **kwargs):
    """Til tanlash."""
    await message.answer(
        "🌐 <b>Tilni tanlang / Выберите язык / Choose language:</b>",
        parse_mode="HTML",
        reply_markup=get_language_keyboard(),
    )


# ——— /brackets ———
@router.message(Command("brackets", "bracket"))
async def cmd_brackets(message: Message, **kwargs):
    """Qavs uslubini tanlash."""
    await message.answer(
        "🗂 <b>Qavs uslubini tanlang:</b>",
        parse_mode="HTML",
        reply_markup=get_bracket_keyboard(),
    )
