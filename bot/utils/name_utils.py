"""
Ism (name) bilan ishlash yordamchi funksiyalari.
"""

import re
from typing import Tuple


# Vaqt tegini topish uchun regex pattern
# [14:30], (14:30), {14:30}, <14:30>, |14:30|, 14:30
TIME_TAG_PATTERN = re.compile(
    r'\s*[\[\(\{<\|]?\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?[\]\)\}>\|]?\s*$',
    re.IGNORECASE
)

# Bracket uslublari
BRACKET_STYLES = {
    "[]": ("[", "]"),
    "()": ("(", ")"),
    "{}": ("{", "}"),
    "<>": ("<", ">"),
    "||": ("|", "|"),
    "none": ("", ""),
}


def strip_time_tag(name: str) -> str:
    """
    Ism oxiridagi vaqt tegini o'chirib tashlaydi.

    Args:
        name: Foydalanuvchi ismi (masalan: 'Ismoil [14:30]')

    Returns:
        str: Vaqt tegisiz ism (masalan: 'Ismoil')

    Examples:
        >>> strip_time_tag("Ismoil [14:30]")
        'Ismoil'
        >>> strip_time_tag("Ismoil (2:30 PM)")
        'Ismoil'
        >>> strip_time_tag("Ismoil")
        'Ismoil'
    """
    result = TIME_TAG_PATTERN.sub("", name).strip()
    return result if result else name.strip()


def add_time_tag(
    name: str,
    time_str: str,
    bracket_style: str = "[]",
    prefix: str = "",
) -> str:
    """
    Ismga vaqt tegini qo'shadi.

    Args:
        name: Asl ism (vaqt tegisiz)
        time_str: Formatlangan vaqt string (masalan: '14:30')
        bracket_style: Qavs uslubi — '[]', '()', '{}', '<>', '||'
        prefix: Vaqtdan oldingi maxsus matn (masalan: '🌙')

    Returns:
        str: Vaqt tegli ism (masalan: 'Ismoil 🌙 [14:30]')
    """
    # Avval eski vaqt tegini olib tashlash
    clean_name = strip_time_tag(name)

    # Bracket olish
    open_br, close_br = BRACKET_STYLES.get(bracket_style, ("[", "]"))

    # Yangi ism yaratish
    parts = [clean_name]
    if prefix:
        parts.append(prefix)
    parts.append(f"{open_br}{time_str}{close_br}")

    result = " ".join(parts)
    return result


def validate_name_length(name: str, max_length: int = 64) -> bool:
    """
    Ism uzunligini tekshiradi (Telegram max 64 belgi).

    Args:
        name: Tekshiriladigan ism
        max_length: Maksimal uzunlik

    Returns:
        bool: Uzunlik limitdan oshmasa True
    """
    return len(name) <= max_length


def extract_original_name(name: str) -> str:
    """
    Ismdan barcha qo'shimchalarni (vaqt tegi, prefix) olib tashlab,
    asl ismni qaytaradi.

    Args:
        name: To'liq ism

    Returns:
        str: Asl ism
    """
    return strip_time_tag(name)


def get_bracket_pair(style: str) -> Tuple[str, str]:
    """Bracket uslubi bo'yicha ochuvchi va yopuvchi belgini qaytaradi."""
    return BRACKET_STYLES.get(style, ("[", "]"))
