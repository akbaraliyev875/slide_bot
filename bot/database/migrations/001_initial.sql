-- 001_initial.sql
-- Dastlabki migratsiya: barcha asosiy jadvallar

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

CREATE TABLE IF NOT EXISTS bans (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    banned_by       INTEGER NOT NULL,
    reason          TEXT,
    banned_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unbanned_at     TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS system_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    level           TEXT NOT NULL,
    message         TEXT NOT NULL,
    user_id         INTEGER,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
