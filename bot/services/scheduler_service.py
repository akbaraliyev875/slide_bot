"""
APScheduler servisi — har foydalanuvchi uchun alohida job boshqarish.
"""

from datetime import datetime
from typing import Optional
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from bot.database.repositories import user_repo, settings_repo


# Global scheduler instansiyasi
scheduler: Optional[AsyncIOScheduler] = None

# Bot ishga tushgan vaqt
bot_start_time: Optional[datetime] = None


def get_scheduler() -> AsyncIOScheduler:
    """Global scheduler ni qaytaradi."""
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler(timezone="UTC")
    return scheduler


async def start_scheduler():
    """
    Scheduler ni ishga tushiradi va mavjud aktiv foydalanuvchilar
    uchun job larni tiklaydi.
    """
    global scheduler, bot_start_time
    import pytz

    scheduler = get_scheduler()
    bot_start_time = datetime.now(pytz.UTC)

    # Mavjud aktiv foydalanuvchilar uchun job lar qo'shish
    active_users = await user_repo.get_all_active_users()
    for user in active_users:
        user_settings = await settings_repo.get_settings(user["id"])
        interval = 1  # default
        if user_settings:
            interval = user_settings.get("update_interval", 1)
        await add_user_job(user["id"], interval)

    if not scheduler.running:
        scheduler.start()
        logger.success(
            f"Scheduler ishga tushdi! {len(active_users)} ta job yuklandi."
        )


async def add_user_job(user_id: int, interval_minutes: int = 1):
    """
    Foydalanuvchi uchun yangilanish job ini qo'shadi.

    Args:
        user_id: Telegram user ID
        interval_minutes: Yangilanish intervali (daqiqalarda)
    """
    global scheduler
    if scheduler is None:
        scheduler = get_scheduler()

    job_id = f"name_update_{user_id}"

    # Agar job allaqachon mavjud bo'lsa, avval o'chirish
    existing = scheduler.get_job(job_id)
    if existing:
        scheduler.remove_job(job_id)

    # Yangi job qo'shish
    from bot.services.name_service import update_user_name
    import pytz

    scheduler.add_job(
        update_user_name,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id=job_id,
        args=[user_id],
        replace_existing=True,
        max_instances=1,
        next_run_time=datetime.now(pytz.utc),  # Darhol ishga tushadi
        misfire_grace_time=120,  # 2 daqiqa kechikishga ruxsat
    )
    logger.info(
        f"Job qo'shildi: {job_id} (har {interval_minutes} daqiqada)"
    )


async def remove_user_job(user_id: int):
    """
    Foydalanuvchi job ini o'chiradi.

    Args:
        user_id: Telegram user ID
    """
    global scheduler
    if scheduler is None:
        return

    job_id = f"name_update_{user_id}"
    try:
        scheduler.remove_job(job_id)
        logger.info(f"Job o'chirildi: {job_id}")
    except Exception:
        logger.debug(f"Job topilmadi: {job_id}")


async def update_user_job(user_id: int, new_interval: int):
    """
    Foydalanuvchi job intervalini o'zgartiradi.

    Args:
        user_id: Telegram user ID
        new_interval: Yangi interval (daqiqalarda)
    """
    await remove_user_job(user_id)
    await add_user_job(user_id, new_interval)
    logger.info(f"Job yangilandi: user_{user_id} → {new_interval} daqiqa")


def get_job_next_run(user_id: int) -> Optional[datetime]:
    """
    Foydalanuvchi job ining keyingi ishga tushish vaqtini qaytaradi.

    Args:
        user_id: Telegram user ID

    Returns:
        datetime: Keyingi ishga tushish vaqti yoki None
    """
    global scheduler
    if scheduler is None:
        return None

    job_id = f"name_update_{user_id}"
    job = scheduler.get_job(job_id)
    if job:
        return job.next_run_time
    return None


def get_active_jobs_count() -> int:
    """Aktiv job lar sonini qaytaradi."""
    global scheduler
    if scheduler is None:
        return 0
    return len(scheduler.get_jobs())


def get_bot_start_time() -> Optional[datetime]:
    """Bot ishga tushgan vaqtni qaytaradi."""
    return bot_start_time


async def shutdown_scheduler():
    """Scheduler ni to'xtatadi."""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler to'xtatildi")
