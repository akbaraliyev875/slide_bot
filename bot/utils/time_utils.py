"""
Vaqt bilan ishlash yordamchi funksiyalari.
"""

from datetime import datetime, timedelta
import pytz


def get_current_time(timezone: str = "Asia/Tashkent") -> datetime:
    """
    Berilgan timezone bo'yicha joriy vaqtni qaytaradi.

    Args:
        timezone: pytz timezone string (masalan: 'Asia/Tashkent')

    Returns:
        datetime: Joriy vaqt berilgan timezone da
    """
    try:
        tz = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        tz = pytz.timezone("Asia/Tashkent")
    return datetime.now(tz)


def format_time(dt: datetime, fmt: str = "HH:MM") -> str:
    """
    datetime obyektini berilgan formatda string ga aylantiradi.

    Args:
        dt: datetime obyekti
        fmt: Format turi — 'HH:MM', 'HH:MM:SS', '12h'

    Returns:
        str: Formatlangan vaqt string

    Examples:
        >>> format_time(dt, "HH:MM")       → "14:30"
        >>> format_time(dt, "HH:MM:SS")    → "14:30:45"
        >>> format_time(dt, "12h")         → "2:30 PM"
    """
    if fmt == "HH:MM":
        return dt.strftime("%H:%M")
    elif fmt == "HH:MM:SS":
        return dt.strftime("%H:%M:%S")
    elif fmt == "12h":
        return dt.strftime("%I:%M %p").lstrip("0")
    else:
        return dt.strftime("%H:%M")


def get_next_update_time(
    interval_minutes: int = 60, timezone: str = "Asia/Tashkent"
) -> datetime:
    """
    Keyingi yangilanish vaqtini hisoblab qaytaradi.

    Args:
        interval_minutes: Yangilanish intervali (daqiqalarda)
        timezone: Foydalanuvchi timezone si

    Returns:
        datetime: Keyingi yangilanish vaqti
    """
    now = get_current_time(timezone)
    return now + timedelta(minutes=interval_minutes)


def format_next_update(
    interval_minutes: int = 60, timezone: str = "Asia/Tashkent"
) -> str:
    """Keyingi yangilanish vaqtini o'qish uchun qulay formatda qaytaradi."""
    next_time = get_next_update_time(interval_minutes, timezone)
    return next_time.strftime("%H:%M")


def get_uptime(start_time: datetime) -> str:
    """
    Bot ishlash vaqtini hisoblaydi va o'qishli formatda qaytaradi.

    Args:
        start_time: Bot ishga tushgan vaqt

    Returns:
        str: '2 kun, 5 soat, 30 daqiqa'
    """
    delta = datetime.now(pytz.UTC) - start_time
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days} kun")
    if hours > 0:
        parts.append(f"{hours} soat")
    parts.append(f"{minutes} daqiqa")

    return ", ".join(parts)


def get_common_timezones() -> list:
    """
    Eng keng tarqalgan timezone larni qaytaradi.
    """
    return [
        "Asia/Tashkent",      # O'zbekiston
        "Asia/Samarkand",     # O'zbekiston (G'arbiy)
        "Europe/Moscow",      # Rossiya
        "Asia/Almaty",        # Qozog'iston
        "Asia/Bishkek",       # Qirg'iziston
        "Asia/Dushanbe",      # Tojikiston
        "Asia/Ashgabat",      # Turkmaniston
        "Asia/Baku",          # Ozarbayjon
        "Asia/Dubai",         # BAA
        "Asia/Istanbul",      # Turkiya
        "Europe/London",      # Buyuk Britaniya
        "America/New_York",   # AQSh (Sharq)
        "America/Los_Angeles",# AQSh (G'arb)
        "Asia/Tokyo",         # Yaponiya
        "Asia/Seoul",         # Janubiy Koreya
        "Europe/Berlin",      # Germaniya
    ]
