"""
🤖 Telegram Profile Name Auto-Updater Bot
==========================================
Kirish nuqtasi — bot va barcha komponentlarni ishga tushiradi.

Stack: Python 3.11+ | Aiogram 3.x | SQLite | APScheduler | Pyrogram
"""

import asyncio
import sys
from pathlib import Path

from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config import settings


# ——— Loguru sozlash ———
def setup_logging():
    """Loguru logger ni sozlash."""
    log_dir = settings.logs_dir

    # Konsol uchun
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
    )

    # Fayl uchun — bot.log
    logger.add(
        str(log_dir / "bot.log"),
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        encoding="utf-8",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} | {message}"
        ),
    )

    # Xatoliklar uchun — errors.log
    logger.add(
        str(log_dir / "errors.log"),
        level="ERROR",
        rotation="5 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
    )


# ——— Bot va Dispatcher yaratish ———
def create_bot() -> Bot:
    """Bot instansiyasini yaratadi."""
    return Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    """Dispatcher yaratadi va router/middleware'larni ulaydi."""
    dp = Dispatcher(storage=MemoryStorage())

    # ——— Middleware'larni ro'yxatdan o'tkazish ———
    from bot.middlewares.throttling import ThrottlingMiddleware
    from bot.middlewares.logging_mw import LoggingMiddleware
    from bot.middlewares.auth import AuthMiddleware
    from bot.middlewares.i18n import LanguageMiddleware

    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(ThrottlingMiddleware(rate_limit=10, period=60))
    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(LanguageMiddleware())

    dp.callback_query.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LanguageMiddleware())

    # ——— Router'larni ulash ———
    from bot.handlers.user import router as user_router
    from bot.handlers.settings import router as settings_router
    from bot.handlers.admin import router as admin_router
    from bot.handlers.callbacks import router as callbacks_router
    from bot.handlers.errors import router as errors_router

    dp.include_router(user_router)
    dp.include_router(settings_router)
    dp.include_router(admin_router)
    dp.include_router(callbacks_router)
    dp.include_router(errors_router)

    return dp


# ——— Asosiy ishga tushirish ———
async def on_startup(bot: Bot):
    """Bot ishga tushganda chaqiriladi."""
    # Database ishga tushirish
    from bot.database.connection import init_db
    await init_db()

    # Til fayllarini yuklash
    from bot.middlewares.i18n import load_translations
    load_translations()

    # Scheduler ishga tushirish
    from bot.services.scheduler_service import start_scheduler
    await start_scheduler()

    # Bot ma'lumotlari
    bot_info = await bot.get_me()
    logger.success(
        f"Bot ishga tushdi! @{bot_info.username} ({bot_info.full_name})"
    )
    logger.info(f"Admin IDs: {settings.ADMIN_IDS}")


async def on_shutdown(bot: Bot):
    """Bot to'xtaganda chaqiriladi."""
    # Scheduler to'xtatish
    from bot.services.scheduler_service import shutdown_scheduler
    await shutdown_scheduler()

    logger.info("Bot to'xtatildi.")


async def main():
    """Asosiy funksiya."""
    setup_logging()
    logger.info("Bot ishga tushirilmoqda...")

    bot = create_bot()
    dp = create_dispatcher()

    # Startup/shutdown hook'lar
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        # Long Polling rejimida ishga tushirish
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot Ctrl+C bilan to'xtatildi.")
    except Exception as e:
        logger.critical(f"Kritik xatolik: {e}")
        raise
