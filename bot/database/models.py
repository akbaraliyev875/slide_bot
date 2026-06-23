"""
Database jadval yaratish moduli — barcha jadvallar shu yerda ta'riflanadi.
"""

import aiosqlite
from loguru import logger

from bot.database.connection import get_db, close_db


# ——— SQL jadval yaratish so'rovlari ———

USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY,
    username        TEXT,
    first_name      TEXT NOT NULL,
    last_name       TEXT,
    original_name   TEXT NOT NULL,
    phone           TEXT,
    is_active       INTEGER DEFAULT 0,
    is_banned       INTEGER DEFAULT 0,
    session_string  TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen       TIMESTAMP
);
"""

USER_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS user_settings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL UNIQUE,
    timezone        TEXT DEFAULT 'Asia/Tashkent',
    time_format     TEXT DEFAULT 'HH:MM',
    bracket_style   TEXT DEFAULT '[]',
    update_interval INTEGER DEFAULT 1,
    prefix_text     TEXT DEFAULT '',
    language        TEXT DEFAULT 'uz',
    notify_daily    INTEGER DEFAULT 0,
    notify_errors   INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

UPDATE_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS update_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    old_name        TEXT,
    new_name        TEXT NOT NULL,
    status          TEXT DEFAULT 'success',
    error_message   TEXT,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

BANS_TABLE = """
CREATE TABLE IF NOT EXISTS bans (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    banned_by       INTEGER NOT NULL,
    reason          TEXT,
    banned_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unbanned_at     TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

SYSTEM_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS system_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    level           TEXT NOT NULL,
    message         TEXT NOT NULL,
    user_id         INTEGER,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Barcha jadvallar ro'yxati
ALL_TABLES = [
    USERS_TABLE,
    USER_SETTINGS_TABLE,
    UPDATE_HISTORY_TABLE,
    BANS_TABLE,
    SYSTEM_LOGS_TABLE,
]


async def create_tables():
    """Barcha jadvallarni yaratadi."""
    db = await get_db()
    try:
        for table_sql in ALL_TABLES:
            await db.execute(table_sql)
        # Eski 60 minutlik default intervalga ega bo'lganlarni 1 minutga o'tkazamiz
        await db.execute("UPDATE user_settings SET update_interval = 1 WHERE update_interval = 60")
        await db.commit()
        logger.info("Barcha jadvallar muvaffaqiyatli yaratildi va interval qiymatlari migratsiya qilindi")
    except Exception as e:
        logger.error(f"Jadval yaratishda xatolik: {e}")
        raise
    finally:
        await close_db(db)
