"""
Reply klaviaturalar — kontakt yuborish va boshqa reply tugmalar.
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqam yuborish tugmasi."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📱 Telefon raqamni yuborish",
                    request_contact=True,
                ),
            ],
            [
                KeyboardButton(text="❌ Bekor qilish"),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Bekor qilish tugmasi."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    """Klaviaturani olib tashlash."""
    return ReplyKeyboardRemove()
