"""
Inline klaviaturalar — settings, language, timezone, format, admin.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils.time_utils import get_common_timezones


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Asosiy menyu inline klaviaturasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔗 Ulash", callback_data="cmd_connect"),
            InlineKeyboardButton(text="📊 Status", callback_data="cmd_status"),
        ],
        [
            InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="cmd_settings"),
            InlineKeyboardButton(text="📈 Statistika", callback_data="cmd_stats"),
        ],
        [
            InlineKeyboardButton(text="📜 Tarix", callback_data="cmd_history"),
            InlineKeyboardButton(text="❓ Yordam", callback_data="cmd_help"),
        ],
    ])


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Sozlamalar inline klaviaturasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🕐 Timezone", callback_data="set_timezone"),
            InlineKeyboardButton(text="📝 Format", callback_data="set_format"),
        ],
        [
            InlineKeyboardButton(text="⏱ Interval", callback_data="set_interval"),
            InlineKeyboardButton(text="✏️ Prefix", callback_data="set_prefix"),
        ],
        [
            InlineKeyboardButton(text="🔔 Bildirishnoma", callback_data="set_notify"),
            InlineKeyboardButton(text="🗂 Qavslar", callback_data="set_brackets"),
        ],
        [
            InlineKeyboardButton(text="🌐 Til", callback_data="set_language"),
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main"),
        ],
    ])


def get_timezone_keyboard() -> InlineKeyboardMarkup:
    """Timezone tanlash klaviaturasi."""
    timezones = get_common_timezones()
    buttons = []
    row = []

    for i, tz in enumerate(timezones):
        # Qisqa nom
        short_name = tz.split("/")[-1].replace("_", " ")
        row.append(
            InlineKeyboardButton(text=short_name, callback_data=f"tz_{tz}")
        )
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="cmd_settings"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_format_keyboard() -> InlineKeyboardMarkup:
    """Vaqt formati tanlash klaviaturasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="14:30 (HH:MM)", callback_data="fmt_HH:MM"),
        ],
        [
            InlineKeyboardButton(text="14:30:45 (HH:MM:SS)", callback_data="fmt_HH:MM:SS"),
        ],
        [
            InlineKeyboardButton(text="2:30 PM (12h)", callback_data="fmt_12h"),
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="cmd_settings"),
        ],
    ])


def get_bracket_keyboard() -> InlineKeyboardMarkup:
    """Bracket uslubi tanlash klaviaturasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="[14:30]", callback_data="br_[]"),
            InlineKeyboardButton(text="(14:30)", callback_data="br_()"),
        ],
        [
            InlineKeyboardButton(text="{14:30}", callback_data="br_{}"),
            InlineKeyboardButton(text="<14:30>", callback_data="br_<>"),
        ],
        [
            InlineKeyboardButton(text="|14:30|", callback_data="br_||"),
            InlineKeyboardButton(text="14:30 (Qavssiz)", callback_data="br_none"),
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="cmd_settings"),
        ],
    ])


def get_interval_keyboard() -> InlineKeyboardMarkup:
    """Yangilanish intervali tanlash klaviaturasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1 daqiqa", callback_data="int_1"),
            InlineKeyboardButton(text="5 daqiqa", callback_data="int_5"),
        ],
        [
            InlineKeyboardButton(text="15 daqiqa", callback_data="int_15"),
            InlineKeyboardButton(text="30 daqiqa", callback_data="int_30"),
        ],
        [
            InlineKeyboardButton(text="1 soat", callback_data="int_60"),
            InlineKeyboardButton(text="2 soat", callback_data="int_120"),
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="cmd_settings"),
        ],
    ])


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Til tanlash klaviaturasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
        ],
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        ],
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="cmd_settings"),
        ],
    ])


def get_notify_keyboard(
    notify_daily: bool = False,
    notify_errors: bool = True,
) -> InlineKeyboardMarkup:
    """Bildirishnoma sozlamalari klaviaturasi."""
    daily_icon = "✅" if notify_daily else "❌"
    errors_icon = "✅" if notify_errors else "❌"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{daily_icon} Kunlik hisobot",
                callback_data="notify_daily",
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"{errors_icon} Xatolik xabarlari",
                callback_data="notify_errors",
            ),
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="cmd_settings"),
        ],
    ])


def get_confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    """Tasdiqlash klaviaturasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data=f"confirm_{action}"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="cancel"),
        ],
    ])


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Admin paneli klaviaturasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users"),
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
        ],
        [
            InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="📋 Loglar", callback_data="admin_logs"),
        ],
        [
            InlineKeyboardButton(text="🚫 Bloklangan", callback_data="admin_banned"),
        ],
    ])
