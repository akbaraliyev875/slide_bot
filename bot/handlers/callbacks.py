"""
Callback query handler'lari — inline tugma bosilganda ishlovchi.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from loguru import logger

from bot.database.repositories import settings_repo, user_repo
from bot.services.scheduler_service import update_user_job
from bot.keyboards.inline import (
    get_main_menu_keyboard,
    get_settings_keyboard,
    get_timezone_keyboard,
    get_format_keyboard,
    get_bracket_keyboard,
    get_interval_keyboard,
    get_language_keyboard,
    get_notify_keyboard,
    get_admin_keyboard,
)
from bot.middlewares.i18n import get_text


# Router yaratish
router = Router(name="callbacks")


# ——— Asosiy menyu callback'lari ———
@router.callback_query(F.data == "back_main")
async def cb_back_main(callback: CallbackQuery, **kwargs):
    """Asosiy menyuga qaytish."""
    await callback.message.edit_reply_markup(
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cb_cancel(callback: CallbackQuery, lang: str = "uz", **kwargs):
    """Bekor qilish."""
    await callback.message.edit_text(get_text("cancel", lang))
    await callback.answer()


# ——— Komanda callback'lari ———
@router.callback_query(F.data == "cmd_settings")
async def cb_settings(callback: CallbackQuery, lang: str = "uz", **kwargs):
    """Sozlamalar menyusiga o'tish."""
    text = get_text("settings_menu", lang)
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "cmd_help")
async def cb_help(callback: CallbackQuery, lang: str = "uz", **kwargs):
    """Yordam ko'rsatish."""
    text = get_text("help_message", lang)
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()


# ——— Sozlamalar callback'lari ———

# Timezone
@router.callback_query(F.data == "set_timezone")
async def cb_set_timezone(callback: CallbackQuery, **kwargs):
    """Timezone menyusini ochish."""
    await callback.message.edit_text(
        "🕐 <b>Vaqt mintaqasini tanlang:</b>",
        parse_mode="HTML",
        reply_markup=get_timezone_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("tz_"))
async def cb_timezone_selected(callback: CallbackQuery, lang: str = "uz", **kwargs):
    """Timezone tanlandi."""
    timezone = callback.data[3:]  # "tz_" ni olib tashlash
    user_id = callback.from_user.id

    await settings_repo.update_settings(user_id, timezone=timezone)

    text = get_text("timezone_changed", lang, timezone=timezone)
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer("✅")


# Format
@router.callback_query(F.data == "set_format")
async def cb_set_format(callback: CallbackQuery, **kwargs):
    """Format menyusini ochish."""
    await callback.message.edit_text(
        "📝 <b>Vaqt formatini tanlang:</b>",
        parse_mode="HTML",
        reply_markup=get_format_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("fmt_"))
async def cb_format_selected(callback: CallbackQuery, lang: str = "uz", **kwargs):
    """Vaqt formati tanlandi."""
    time_format = callback.data[4:]  # "fmt_" ni olib tashlash
    user_id = callback.from_user.id

    await settings_repo.update_settings(user_id, time_format=time_format)

    text = get_text("format_changed", lang, format=time_format)
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer("✅")


# Bracket style
@router.callback_query(F.data == "set_brackets")
async def cb_set_brackets(callback: CallbackQuery, **kwargs):
    """Qavslar menyusini ochish."""
    await callback.message.edit_text(
        "🗂 <b>Qavs uslubini tanlang:</b>",
        parse_mode="HTML",
        reply_markup=get_bracket_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("br_"))
async def cb_bracket_selected(callback: CallbackQuery, lang: str = "uz", **kwargs):
    """Bracket uslubi tanlandi."""
    bracket_style = callback.data[3:]  # "br_" ni olib tashlash
    user_id = callback.from_user.id

    await settings_repo.update_settings(user_id, bracket_style=bracket_style)

    style_display = "Qavssiz (none)" if bracket_style == "none" else bracket_style
    await callback.message.edit_text(
        f"✅ Qavs uslubi o'zgartirildi: <b>{style_display}</b>",
        parse_mode="HTML",
    )
    await callback.answer("✅")


# Interval
@router.callback_query(F.data == "set_interval")
async def cb_set_interval(callback: CallbackQuery, **kwargs):
    """Interval menyusini ochish."""
    await callback.message.edit_text(
        "⏱ <b>Yangilanish intervalini tanlang:</b>",
        parse_mode="HTML",
        reply_markup=get_interval_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("int_"))
async def cb_interval_selected(callback: CallbackQuery, lang: str = "uz", **kwargs):
    """Interval tanlandi."""
    interval = int(callback.data[4:])  # "int_" ni olib tashlash
    user_id = callback.from_user.id

    await settings_repo.update_settings(user_id, update_interval=interval)
    await update_user_job(user_id, interval)

    text = get_text("interval_changed", lang, interval=interval)
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer("✅")


# Language
@router.callback_query(F.data == "set_language")
async def cb_set_language(callback: CallbackQuery, **kwargs):
    """Til menyusini ochish."""
    await callback.message.edit_text(
        "🌐 <b>Tilni tanlang / Выберите язык / Choose language:</b>",
        parse_mode="HTML",
        reply_markup=get_language_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lang_"))
async def cb_language_selected(callback: CallbackQuery, **kwargs):
    """Til tanlandi."""
    language = callback.data[5:]  # "lang_" ni olib tashlash
    user_id = callback.from_user.id

    await settings_repo.update_settings(user_id, language=language)

    text = get_text("language_changed", language)
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer("✅")


# Notify
@router.callback_query(F.data == "set_notify")
async def cb_set_notify(callback: CallbackQuery, **kwargs):
    """Bildirishnoma menyusini ochish."""
    user_id = callback.from_user.id
    user_settings = await settings_repo.get_settings(user_id)

    notify_daily = bool(user_settings.get("notify_daily", 0)) if user_settings else False
    notify_errors = bool(user_settings.get("notify_errors", 1)) if user_settings else True

    await callback.message.edit_text(
        "🔔 <b>Bildirishnoma sozlamalari:</b>",
        parse_mode="HTML",
        reply_markup=get_notify_keyboard(notify_daily, notify_errors),
    )
    await callback.answer()


@router.callback_query(F.data == "notify_daily")
async def cb_toggle_daily(callback: CallbackQuery, lang: str = "uz", **kwargs):
    """Kunlik hisobot toggle."""
    user_id = callback.from_user.id
    user_settings = await settings_repo.get_settings(user_id)
    current = bool(user_settings.get("notify_daily", 0)) if user_settings else False

    await settings_repo.update_settings(user_id, notify_daily=int(not current))

    notify_errors = bool(user_settings.get("notify_errors", 1)) if user_settings else True
    await callback.message.edit_reply_markup(
        reply_markup=get_notify_keyboard(not current, notify_errors),
    )
    await callback.answer(get_text("notify_updated", lang))


@router.callback_query(F.data == "notify_errors")
async def cb_toggle_errors(callback: CallbackQuery, lang: str = "uz", **kwargs):
    """Xatolik xabarlari toggle."""
    user_id = callback.from_user.id
    user_settings = await settings_repo.get_settings(user_id)
    current = bool(user_settings.get("notify_errors", 1)) if user_settings else True

    await settings_repo.update_settings(user_id, notify_errors=int(not current))

    notify_daily = bool(user_settings.get("notify_daily", 0)) if user_settings else False
    await callback.message.edit_reply_markup(
        reply_markup=get_notify_keyboard(notify_daily, not current),
    )
    await callback.answer(get_text("notify_updated", lang))


# ——— Admin callback'lari ———
@router.callback_query(F.data == "admin_users")
async def cb_admin_users(callback: CallbackQuery, **kwargs):
    """Foydalanuvchilar ro'yxati (admin)."""
    counts = await user_repo.get_users_count()
    await callback.message.edit_text(
        f"👥 <b>Foydalanuvchilar</b>\n\n"
        f"📊 Jami: <b>{counts['total']}</b>\n"
        f"✅ Aktiv: <b>{counts['active']}</b>\n"
        f"🚫 Bloklangan: <b>{counts['banned']}</b>",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_banned")
async def cb_admin_banned(callback: CallbackQuery, **kwargs):
    """Bloklangan foydalanuvchilar ro'yxati."""
    from bot.database.repositories import ban_repo as br

    banned = await br.get_all_banned_users()
    if not banned:
        text = "🚫 Bloklangan foydalanuvchilar yo'q."
    else:
        lines = []
        for b in banned:
            lines.append(
                f"• {b.get('first_name', '?')}"
                f" (ID: {b['id']}) — {b.get('reason', '—')}"
            )
        text = "🚫 <b>Bloklangan foydalanuvchilar:</b>\n\n" + "\n".join(lines)

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery, **kwargs):
    """Umumiy statistika (admin)."""
    from bot.database.repositories import history_repo as hr

    counts = await user_repo.get_users_count()
    all_users = await user_repo.get_all_users()

    today_total = 0
    for u in all_users:
        today_total += await hr.get_today_count(u["id"])

    await callback.message.edit_text(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{counts['total']}</b>\n"
        f"✅ Aktiv: <b>{counts['active']}</b>\n"
        f"🚫 Bloklangan: <b>{counts['banned']}</b>\n"
        f"📅 Bugungi yangilanishlar: <b>{today_total}</b>",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, lang: str = "uz", **kwargs):
    """Broadcast xabari yuborish (admin)."""
    await callback.message.answer(
        "📢 Barcha foydalanuvchilarga xabar yuborish uchun:\n"
        "<code>/broadcast Xabar matni</code>",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_logs")
async def cb_admin_logs(callback: CallbackQuery, **kwargs):
    """So'nggi loglarni ko'rish (admin)."""
    import os
    log_path = "logs/bot.log"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        last_lines = lines[-20:] if len(lines) >= 20 else lines
        log_text = "".join(last_lines).strip()
        text = f"📋 <b>So'nggi loglar:</b>\n\n<pre>{log_text[:3000]}</pre>"
    else:
        text = "📋 Log fayl topilmadi."
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


# ——— Menyu komanda callback'lari ———
@router.callback_query(F.data == "cmd_connect")
async def cb_connect(callback: CallbackQuery, lang: str = "uz", **kwargs):
    """Connect buyrug'ini ishga tushirish."""
    await callback.message.answer("/connect buyrug'ini yuboring.")
    await callback.answer()


@router.callback_query(F.data == "cmd_status")
async def cb_status(callback: CallbackQuery, lang: str = "uz", **kwargs):
    """Status buyrug'ini ishga tushirish."""
    await callback.message.answer("/status buyrug'ini yuboring.")
    await callback.answer()


@router.callback_query(F.data == "cmd_stats")
async def cb_stats(callback: CallbackQuery, **kwargs):
    """Stats buyrug'ini ishga tushirish."""
    await callback.message.answer("/stats buyrug'ini yuboring.")
    await callback.answer()


@router.callback_query(F.data == "cmd_history")
async def cb_history(callback: CallbackQuery, **kwargs):
    """History buyrug'ini ishga tushirish."""
    await callback.message.answer("/history buyrug'ini yuboring.")
    await callback.answer()
