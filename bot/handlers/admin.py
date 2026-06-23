"""
Admin handler'lari — admin panel, broadcast, ban/unban, logs.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from bot.utils.decorators import admin_only
from bot.database.repositories import user_repo, ban_repo, history_repo
from bot.services.notification_service import broadcast_message
from bot.services.scheduler_service import remove_user_job
from bot.keyboards.inline import get_admin_keyboard
from bot.keyboards.reply import get_cancel_keyboard, remove_keyboard
from bot.middlewares.i18n import get_text
from config import settings


# Router yaratish
router = Router(name="admin")


# FSM States
class BroadcastStates(StatesGroup):
    waiting_message = State()


class BanStates(StatesGroup):
    waiting_user_id = State()
    waiting_reason = State()


# ——— /admin ———
@router.message(Command("admin"))
@admin_only
async def cmd_admin(message: Message, lang: str = "uz", **kwargs):
    """Admin paneli."""
    counts = await user_repo.get_users_count()

    # Bugungi yangilanishlar (barcha foydalanuvchilar)
    today_updates = 0
    all_users = await user_repo.get_all_users()
    for u in all_users:
        today_updates += await history_repo.get_today_count(u["id"])

    text = get_text(
        "admin_panel", lang,
        total=counts["total"],
        active=counts["active"],
        banned=counts["banned"],
        today_updates=today_updates,
    )
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )


# ——— /broadcast ———
@router.message(Command("broadcast"))
@admin_only
async def cmd_broadcast(message: Message, state: FSMContext, lang: str = "uz", **kwargs):
    """Ommaviy xabar yuborish."""
    await message.answer(
        get_text("broadcast_prompt", lang),
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(BroadcastStates.waiting_message)


@router.message(BroadcastStates.waiting_message, F.text)
@admin_only
async def process_broadcast(message: Message, state: FSMContext, lang: str = "uz", **kwargs):
    """Broadcast xabarini qayta ishlash."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            get_text("cancel", lang),
            reply_markup=remove_keyboard(),
        )
        return

    # Barcha foydalanuvchilarga yuborish
    all_users = await user_repo.get_all_users()
    user_ids = [u["id"] for u in all_users if not u.get("is_banned")]

    await message.answer("📢 Yuborilmoqda...", reply_markup=remove_keyboard())

    result = await broadcast_message(
        bot=message.bot,
        user_ids=user_ids,
        text=message.text,
    )

    text = get_text(
        "broadcast_result", lang,
        success=result["success"],
        failed=result["failed"],
    )
    await message.answer(text, parse_mode="HTML")
    await state.clear()


# ——— /ban ———
@router.message(Command("ban"))
@admin_only
async def cmd_ban(message: Message, lang: str = "uz", **kwargs):
    """Foydalanuvchini bloklash."""
    args = message.text.split(maxsplit=2)

    if len(args) < 3:
        await message.answer(
            "❌ <b>Foydalanish:</b> /ban [user_id] [sabab]\n"
            "Masalan: <code>/ban 123456789 Spam</code>",
            parse_mode="HTML",
        )
        return

    try:
        target_user_id = int(args[1])
    except ValueError:
        await message.answer("❌ User ID noto'g'ri!")
        return

    reason = args[2]
    admin_id = message.from_user.id

    # Bloklash
    success = await ban_repo.ban_user(target_user_id, admin_id, reason)

    if success:
        # Scheduler job o'chirish
        await remove_user_job(target_user_id)

        # Bloklangan foydalanuvchiga xabar
        try:
            await message.bot.send_message(
                chat_id=target_user_id,
                text=f"⛔ Sizning akkauntingiz bloklandi.\nSabab: {reason}",
            )
        except Exception:
            pass

        text = get_text("ban_success", lang, user_id=target_user_id, reason=reason)
        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer("❌ Bloklashda xatolik!")


# ——— /unban ———
@router.message(Command("unban"))
@admin_only
async def cmd_unban(message: Message, lang: str = "uz", **kwargs):
    """Foydalanuvchi blokini ochish."""
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer(
            "❌ <b>Foydalanish:</b> /unban [user_id]\n"
            "Masalan: <code>/unban 123456789</code>",
            parse_mode="HTML",
        )
        return

    try:
        target_user_id = int(args[1])
    except ValueError:
        await message.answer("❌ User ID noto'g'ri!")
        return

    success = await ban_repo.unban_user(target_user_id)

    if success:
        text = get_text("unban_success", lang, user_id=target_user_id)
        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer("❌ Blok ochishda xatolik!")


# ——— /logs ———
@router.message(Command("logs"))
@admin_only
async def cmd_logs(message: Message, **kwargs):
    """Tizim jurnalini ko'rish."""
    try:
        log_path = settings.logs_dir / "bot.log"
        if not log_path.exists():
            await message.answer("📋 Log fayl bo'sh yoki mavjud emas.")
            return

        # Oxirgi 50 qator
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        last_lines = lines[-50:] if len(lines) > 50 else lines
        log_text = "".join(last_lines)

        if len(log_text) > 4000:
            log_text = log_text[-4000:]

        await message.answer(
            f"📋 <b>Oxirgi loglar:</b>\n\n<pre>{log_text}</pre>",
            parse_mode="HTML",
        )
    except Exception as e:
        await message.answer(f"❌ Loglarni o'qishda xatolik: {e}")
