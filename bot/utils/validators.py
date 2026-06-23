"""
Kiritma tekshirish (validatsiya) funksiyalari.
"""

import pytz


# Ruxsat etilgan vaqt formatlari
VALID_TIME_FORMATS = ["HH:MM", "HH:MM:SS", "12h"]

# Ruxsat etilgan bracket uslublari
VALID_BRACKET_STYLES = ["[]", "()", "{}", "<>", "||", "none"]

# Ruxsat etilgan tillar
VALID_LANGUAGES = ["uz", "ru", "en"]

# Interval chegaralari (daqiqalarda)
MIN_INTERVAL = 1
MAX_INTERVAL = 1440  # 24 soat

# Prefix maksimal uzunligi
MAX_PREFIX_LENGTH = 20


def validate_timezone(timezone: str) -> bool:
    """
    Timezone to'g'ri ekanligini tekshiradi.

    Args:
        timezone: pytz timezone string

    Returns:
        bool: To'g'ri bo'lsa True
    """
    return timezone in pytz.all_timezones


def validate_interval(interval: int) -> bool:
    """
    Yangilanish intervalini tekshiradi.

    Args:
        interval: Daqiqalardagi interval

    Returns:
        bool: To'g'ri oraliqda bo'lsa True
    """
    return MIN_INTERVAL <= interval <= MAX_INTERVAL


def validate_format(time_format: str) -> bool:
    """
    Vaqt formatini tekshiradi.

    Args:
        time_format: Vaqt formati string

    Returns:
        bool: Ruxsat etilgan format bo'lsa True
    """
    return time_format in VALID_TIME_FORMATS


def validate_bracket_style(style: str) -> bool:
    """
    Bracket uslubini tekshiradi.

    Args:
        style: Bracket uslubi string

    Returns:
        bool: Ruxsat etilgan uslub bo'lsa True
    """
    return style in VALID_BRACKET_STYLES


def validate_language(lang: str) -> bool:
    """
    Til kodini tekshiradi.

    Args:
        lang: Til kodi ('uz', 'ru', 'en')

    Returns:
        bool: Ruxsat etilgan til bo'lsa True
    """
    return lang in VALID_LANGUAGES


def validate_prefix(prefix: str) -> bool:
    """
    Prefix matnini tekshiradi.

    Args:
        prefix: Prefix matn

    Returns:
        bool: Uzunligi limitdan oshmasa True
    """
    return len(prefix) <= MAX_PREFIX_LENGTH
