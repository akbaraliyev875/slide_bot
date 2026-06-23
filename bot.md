# 🤖 Telegram Profile Name Auto-Updater Bot — To'liq Arxitektura Hujjati

> **Versiya:** 1.0.0  
> **Stack:** Python 3.11+ | Aiogram 3.x | SQLite | APScheduler  
> **Maqsad:** Foydalanuvchi Telegram profil ismining oxiriga avtomatik ravishda joriy soatni qo'shib turuvchi bot

---

## 📋 MUNDARIJA

1. [Loyiha Tavsifi](#loyiha-tavsifi)
2. [Funksiyalar Ro'yxati (20+)](#funksiyalar-royxati)
3. [Arxitektura Diagrammasi](#arxitektura-diagrammasi)
4. [Papka Tuzilmasi](#papka-tuzilmasi)
5. [Ma'lumotlar Bazasi Sxemasi](#malumotlar-bazasi-sxemasi)
6. [Modul Tavsiflari](#modul-tavsiflari)
7. [API va Konfiguratsiya](#api-va-konfiguratsiya)
8. [Xavfsizlik](#xavfsizlik)
9. [Deploy va CI/CD](#deploy-va-cicd)
10. [Kelajak Rejalar](#kelajak-rejalar)

---

## 🎯 LOYIHA TAVSIFI

Bu bot Telegram foydalanuvchilarining profil ismiga **har soatda avtomatik ravishda joriy vaqtni** qo'shib turadi. Masalan:

```
Ismoil  →  Ismoil [14:00]
Ismoil [14:00]  →  Ismoil [15:00]
```

**Asosiy Texnologiyalar:**

| Texnologiya | Versiya | Maqsad |
|-------------|---------|--------|
| Python | 3.11+ | Asosiy dasturlash tili |
| Aiogram | 3.7+ | Telegram Bot Framework |
| SQLite | 3.x | Ma'lumotlar bazasi |
| APScheduler | 3.10+ | Vazifalar rejalashtiruvchi |
| aiohttp | 3.9+ | Asinxron HTTP so'rovlar |
| python-dotenv | 1.0+ | Muhit o'zgaruvchilari |

---

## ✅ FUNKSIYALAR RO'YXATI

### 🔑 ASOSIY FUNKSIYALAR (Core)

#### 1. `/start` — Botni Ishga Tushirish
- Foydalanuvchini DB ga ro'yxatdan o'tkazadi
- Profil rasm mavjudligini tekshiradi
- Telegram API orqali joriy ism o'qiladi
- Xush kelibsiz xabari yuboriladi

#### 2. `/connect` — Profilni Ulash
- Foydalanuvchi akkauntini botga ulaydi
- `user_access_hash` saqlanadi
- Userbot sessiyasi boshlanadi
- Ulanish holati DB ga yoziladi

#### 3. `/disconnect` — Profilni Uzish
- Aktiv sessiya to'xtatiladi
- Ism dastlabki holatga qaytariladi
- DB dagi `is_active = 0` qilinadi
- Tasdiqlash xabari yuboriladi

#### 4. Auto Name Updater (Scheduler Job)
- Har soatda bir marta ishlaydi
- Joriy vaqtni `HH:MM` formatida oladi
- Regex orqali eski vaqt tagini o'chiradi
- Yangi ism `{original_name} [HH:MM]` ko'rinishida yangilanadi

#### 5. `/status` — Bot Holati
- Ulanish holatini ko'rsatadi
- Keyingi yangilanish vaqtini ko'rsatadi
- Necha marta yangilangani statistikasi
- Sessiya muddati ko'rsatiladi

### ⚙️ SOZLAMALAR FUNKSIYALARI (Settings)

#### 6. `/settings` — Sozlamalar Menyusi
- Inline klaviatura orqali interaktiv menyu
- Vaqt formati tanlash (`HH:MM`, `HH:MM:SS`, `12h/24h`)
- Timezone tanlash (dunyoning istalgan mintaqasi)
- Yangilanish intervali (30 daqiqa, 1 soat, 2 soat, 6 soat)

#### 7. `/timezone` — Vaqt Mintaqasini O'zgartirish
- Inline qidirish orqali shahar/mamlakat tanlash
- `pytz` kutubxonasi bilan ishlaydi
- O'zgarish darhol kuchga kiradi
- DB ga saqlanadi

#### 8. `/format` — Vaqt Formatini Belgilash
- 12 soatlik yoki 24 soatlik format
- Faqat soat (`[14h]`), soat:daqiqa (`[14:30]`), soat:daqiqa:soniya (`[14:30:45]`)
- Maxsus belgilar: `[ ]`, `( )`, `{ }`, `< >`, `| |`

#### 9. `/interval` — Yangilanish Intervalini O'zgartirish
- Minimal: 15 daqiqa
- Maksimal: 24 soat
- Botni yuklamaslik uchun throttle
- Hisob-kitob: soatiga necha API chaqiruv

#### 10. `/prefix` — Qo'shimcha Matn Prefiksi
- Vaqtdan oldin maxsus matn qo'shish
- Masalan: `Ismoil 🌙 [23:00]`
- Emoji qo'shish imkoniyati
- Belgilar chegarasi: 20 belgi

### 📊 STATISTIKA FUNKSIYALARI (Analytics)

#### 11. `/stats` — Shaxsiy Statistika
- Jami yangilanishlar soni
- Bugun nechta yangilangan
- Eng ko'p faol bo'lgan vaqt oralig'i
- Botdan foydalanish davomiyligi (kun/soat)

#### 12. `/history` — Yangilanish Tarixi
- Oxirgi 10 ta yangilanish ro'yxati
- Sana va vaqt bilan
- Muvaffaqiyatli / xatoliklar ajratilgan
- Export CSV ga yuklab olish

#### 13. `/uptime` — Bot Ishlash Vaqti
- Bot necha kun/soat ishlayotgani
- Scheduler statusini ko'rsatadi
- Oxirgi xatolik ro'yxati (agar bo'lsa)

### 🔔 BILDIRISHNOMA FUNKSIYALARI (Notifications)

#### 14. `/notify` — Bildirishnomalar Sozlamalari
- Har kuni hisobot olish (on/off)
- Xatolik yuzaga kelganda xabar berish
- Sessiya tugashi haqida ogohlantirishlar
- Telegram kanal orqali ham xabar berish imkoniyati

#### 15. `/reminder` — Eslatma Tizimi
- "Bugungi statistika" kunlik xabar
- Sessiya muddati tugayotgan haqida ogohlantirish (3 kun oldin)
- Yangilanish soni maqsadiga yetganda tabriklash

### 🛡️ XAVFSIZLIK FUNKSIYALARI (Security)

#### 16. `/session` — Sessiya Boshqaruvi
- Aktiv sessiya ma'lumotlari
- Oxirgi kirish vaqti va IP (agar mavjud)
- Sessiyani yangilash
- Barcha sessiyalardan chiqish

#### 17. `/revoke` — Sessiyani Bekor Qilish
- Maxsus sessiyani bekor qilish
- Barcha qurilmalardan chiqish
- Xavfsizlik sababi: shubhali faoliyat

#### 18. Flood Control va Rate Limiting
- Bir foydalanuvchidan juda ko'p so'rov kelib tushmasligi uchun
- 1 daqiqada maksimal 10 ta komanda
- Global throttle middleware

### 👑 ADMIN FUNKSIYALARI (Admin Panel)

#### 19. `/admin` — Admin Paneli
- Jami foydalanuvchilar soni
- Aktif/nofaol foydalanuvchilar nisbati
- Kunlik yangilanishlar grafigi (matn ko'rinishida)
- Xatoliklar jurnali

#### 20. `/broadcast` — Ommaviy Xabar Yuborish
- Barcha foydalanuvchilarga yoki guruhga xabar
- Markdown va HTML formatlash
- Inline tugmalar bilan xabar
- Yuborish jarayonini ko'rsatish (progress bar)

#### 21. `/ban` & `/unban` — Foydalanuvchini Bloklash
- Sababini yozish majburiy
- Bloklangan foydalanuvchiga avto-xabar
- Blok tarixi saqlanadi

#### 22. `/logs` — Tizim Jurnali
- Real vaqtda log fayli ko'rish
- Filtr: xatoliklar, ogohlantirishlar, ma'lumotlar
- Loglarni yuklab olish (`.txt` format)

### 🌐 QO'SHIMCHA FUNKSIYALAR (Extras)

#### 23. `/help` — Yordam
- Barcha komandalar ro'yxati
- Har bir komanda uchun qisqa tavsif
- Inline tugmalar orqali kategoriyalash
- Video yo'riqnoma havolasi

#### 24. `/language` — Interfeys Tili
- O'zbek, Rus, Ingliz tili tanlash
- Barcha xabarlar tanlangan tilda
- `gettext` / `i18n` tizimi bilan

#### 25. `/feedback` — Muammo Xabari / Taklif
- Foydalanuvchi xabar yozib yuboradi
- Admin albatta ko'radi
- Javob berish imkoniyati

---

## 🏗️ ARXITEKTURA DIAGRAMMASI

```
┌─────────────────────────────────────────────────────────────┐
│                     TELEGRAM SERVERS                        │
│                  (MTProto / Bot API)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │ Updates (Webhook / Long Polling)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    BOT APPLICATION                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  main.py (Entry Point)               │   │
│  │   - Bot & Dispatcher initialization                  │   │
│  │   - Middleware registration                          │   │
│  │   - Router inclusion                                 │   │
│  │   - Scheduler startup                               │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │                MIDDLEWARE LAYER                      │   │
│  │   - ThrottlingMiddleware (Rate Limit)                │   │
│  │   - LoggingMiddleware                                │   │
│  │   - AuthMiddleware (Ban Check)                       │   │
│  │   - LanguageMiddleware (i18n)                        │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │                  ROUTERS                             │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │   │
│  │  │  user.py    │  │  settings.py │  │  admin.py  │  │   │
│  │  │ /start      │  │ /timezone    │  │ /admin     │  │   │
│  │  │ /connect    │  │ /format      │  │ /broadcast │  │   │
│  │  │ /disconnect │  │ /interval    │  │ /ban       │  │   │
│  │  │ /status     │  │ /prefix      │  │ /logs      │  │   │
│  │  │ /stats      │  │ /notify      │  │            │  │   │
│  │  │ /history    │  │ /language    │  │            │  │   │
│  │  │ /help       │  │ /feedback    │  │            │  │   │
│  │  │ /session    │  │              │  │            │  │   │
│  │  └─────────────┘  └──────────────┘  └────────────┘  │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │               SERVICE LAYER                          │   │
│  │  ┌──────────────────┐    ┌─────────────────────────┐ │   │
│  │  │  NameService     │    │  SchedulerService       │ │   │
│  │  │  - update_name() │    │  - add_job()            │ │   │
│  │  │  - get_name()    │    │  - remove_job()         │ │   │
│  │  │  - parse_name()  │    │  - update_job()         │ │   │
│  │  └──────────────────┘    └─────────────────────────┘ │   │
│  │  ┌──────────────────┐    ┌─────────────────────────┐ │   │
│  │  │  UserService     │    │  NotificationService    │ │   │
│  │  │  - get_user()    │    │  - send_daily_report()  │ │   │
│  │  │  - update_user() │    │  - send_error_alert()   │ │   │
│  │  │  - create_user() │    │  - send_reminder()      │ │   │
│  │  └──────────────────┘    └─────────────────────────┘ │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │              DATABASE LAYER (SQLite)                 │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │   │
│  │  │  users   │  │ settings │  │  update_history  │   │   │
│  │  │  table   │  │  table   │  │     table        │   │   │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │   │
│  │  ┌──────────┐  ┌──────────┐                          │   │
│  │  │  bans    │  │   logs   │                          │   │
│  │  │  table   │  │  table   │                          │   │
│  │  └──────────┘  └──────────┘                          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              APScheduler                             │   │
│  │   AsyncIOScheduler → Har foydalanuvchi uchun         │   │
│  │   alohida Job (cron / interval trigger)              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│            TELEGRAM USER API (Pyrogram/Telethon)            │
│         Foydalanuvchi nomidan profil yangilash               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 PAPKA TUZILMASI

```
telegram-name-bot/
│
├── 📄 main.py                    # Entry point
├── 📄 config.py                  # Konfiguratsiya va env o'zgaruvchilari
├── 📄 requirements.txt           # Dependencylar
├── 📄 .env                       # Maxfiy kalitlar (gitignore)
├── 📄 .env.example               # Namuna env fayli
├── 📄 .gitignore
├── 📄 Dockerfile                 # Docker konfiguratsiyasi
├── 📄 docker-compose.yml
├── 📄 README.md
│
├── 📁 bot/
│   ├── 📄 __init__.py
│   │
│   ├── 📁 handlers/              # Router / Handler modullar
│   │   ├── 📄 __init__.py
│   │   ├── 📄 user.py            # Asosiy foydalanuvchi komandalar
│   │   ├── 📄 settings.py        # Sozlamalar komandalar
│   │   ├── 📄 admin.py           # Admin komandalar
│   │   ├── 📄 callbacks.py       # Inline tugma callback'lari
│   │   └── 📄 errors.py          # Xatoliklarni ushlash
│   │
│   ├── 📁 middlewares/           # Middleware'lar
│   │   ├── 📄 __init__.py
│   │   ├── 📄 throttling.py      # Rate limiting
│   │   ├── 📄 logging.py         # So'rovlarni loglash
│   │   ├── 📄 auth.py            # Ban tekshirish
│   │   └── 📄 i18n.py            # Tilni o'rnatish
│   │
│   ├── 📁 services/              # Biznes mantiq
│   │   ├── 📄 __init__.py
│   │   ├── 📄 name_service.py    # Nom yangilash logikasi
│   │   ├── 📄 user_service.py    # Foydalanuvchi operatsiyalari
│   │   ├── 📄 scheduler_service.py # APScheduler menejeri
│   │   └── 📄 notification_service.py # Bildirishnomalar
│   │
│   ├── 📁 database/              # Database qatlam
│   │   ├── 📄 __init__.py
│   │   ├── 📄 connection.py      # SQLite ulanish (aiosqlite)
│   │   ├── 📄 models.py          # Jadval definitsiyalari
│   │   ├── 📄 migrations/        # DB migratsiyalar
│   │   │   ├── 📄 001_initial.sql
│   │   │   └── 📄 002_add_settings.sql
│   │   └── 📁 repositories/      # Repository pattern
│   │       ├── 📄 user_repo.py
│   │       ├── 📄 settings_repo.py
│   │       ├── 📄 history_repo.py
│   │       └── 📄 ban_repo.py
│   │
│   ├── 📁 keyboards/             # Telegram klaviaturalar
│   │   ├── 📄 __init__.py
│   │   ├── 📄 inline.py          # Inline klaviaturalar
│   │   └── 📄 reply.py           # Reply klaviaturalar
│   │
│   ├── 📁 utils/                 # Yordamchi funksiyalar
│   │   ├── 📄 __init__.py
│   │   ├── 📄 time_utils.py      # Vaqt formatlash
│   │   ├── 📄 name_utils.py      # Ism tahlil/o'zgartirish
│   │   ├── 📄 validators.py      # Kiritma tekshirish
│   │   └── 📄 decorators.py      # Dekoratorlar (admin_only, etc.)
│   │
│   └── 📁 locales/               # Tillar (i18n)
│       ├── 📄 uz.json            # O'zbek tili
│       ├── 📄 ru.json            # Rus tili
│       └── 📄 en.json            # Ingliz tili
│
├── 📁 tests/                     # Unit va Integration testlar
│   ├── 📄 test_name_service.py
│   ├── 📄 test_time_utils.py
│   └── 📄 test_database.py
│
└── 📁 logs/                      # Log fayllar
    ├── 📄 bot.log
    └── 📄 errors.log
```

---

## 🗄️ MA'LUMOTLAR BAZASI SXEMASI

### Jadval 1: `users`
```sql
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY,          -- Telegram user ID
    username        TEXT,                         -- @username (nullable)
    first_name      TEXT NOT NULL,                -- Asl ism
    last_name       TEXT,                         -- Familiya (nullable)
    original_name   TEXT NOT NULL,                -- Vaqt qo'shilmagan asl to'liq ism
    phone           TEXT,                         -- Telefon raqam
    is_active       INTEGER DEFAULT 0,            -- 1=ulangan, 0=uzilgan
    is_banned       INTEGER DEFAULT 0,            -- 1=bloklangan
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen       TIMESTAMP
);
```

### Jadval 2: `user_settings`
```sql
CREATE TABLE IF NOT EXISTS user_settings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL UNIQUE,
    timezone        TEXT DEFAULT 'Asia/Tashkent', -- pytz timezone string
    time_format     TEXT DEFAULT 'HH:MM',         -- HH:MM | HH:MM:SS | 12h
    bracket_style   TEXT DEFAULT '[]',            -- [] () {} <> ||
    update_interval INTEGER DEFAULT 1,            -- Daqiqalarda
    prefix_text     TEXT DEFAULT '',              -- Vaqtdan oldingi matn
    language        TEXT DEFAULT 'uz',            -- uz | ru | en
    notify_daily    INTEGER DEFAULT 0,            -- Kunlik hisobot
    notify_errors   INTEGER DEFAULT 1,            -- Xatolik xabari
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Jadval 3: `update_history`
```sql
CREATE TABLE IF NOT EXISTS update_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    old_name        TEXT,                         -- Oldingi ism
    new_name        TEXT NOT NULL,                -- Yangi ism
    status          TEXT DEFAULT 'success',       -- success | failed
    error_message   TEXT,                         -- Xatolik xabari (agar bo'lsa)
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Jadval 4: `bans`
```sql
CREATE TABLE IF NOT EXISTS bans (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    banned_by       INTEGER NOT NULL,             -- Admin ID
    reason          TEXT,
    banned_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unbanned_at     TIMESTAMP,                    -- NULL = hali bloklangan
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Jadval 5: `system_logs`
```sql
CREATE TABLE IF NOT EXISTS system_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    level           TEXT NOT NULL,               -- DEBUG | INFO | WARNING | ERROR
    message         TEXT NOT NULL,
    user_id         INTEGER,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📦 MODUL TAVSIFLARI

### `main.py` — Kirish Nuqtasi
```python
# Vazifalar:
# 1. Bot va Dispatcher yaratish
# 2. Middleware'larni ro'yxatdan o'tkazish
# 3. Router'larni ulash
# 4. Database'ni ishga tushirish
# 5. APScheduler'ni ishga tushirish
# 6. Webhook yoki Long Polling ishga tushirish
```

### `bot/services/name_service.py` — Asosiy Mantiq
```python
# Vazifalar:
# - update_user_name(user_id, bot) -> bool
#   * DB dan foydalanuvchi ma'lumotlarini olish
#   * Joriy vaqtni timezone bo'yicha hisoblash
#   * Vaqt formatini settings bo'yicha formatlash
#   * Eski vaqt tegini regex bilan o'chirish:
#       pattern = r'\s*[\[\(\{\<\|]?\d{1,2}:\d{2}(:\d{2})?[\]\)\}\>\|]?\s*$'
#   * Yangi ismni qo'llash: f"{original_name} {bracket[0]}{time_str}{bracket[1]}"
#   * Telegram User API orqali yangilash
#   * Natijani history ga yozish
```

### `bot/services/scheduler_service.py` — Vazifalar Rejalashtiruvchi
```python
# Vazifalar:
# - start_scheduler() -> AsyncIOScheduler
# - add_user_job(user_id, interval_minutes)
# - remove_user_job(user_id)
# - update_user_job(user_id, new_interval)
# - get_job_next_run(user_id) -> datetime
```

### `bot/utils/time_utils.py` — Vaqt Yordamchisi
```python
# Funksiyalar:
# - get_current_time(timezone: str) -> datetime
# - format_time(dt: datetime, fmt: str) -> str
#   Formatlar: "HH:MM" -> "14:30"
#              "HH:MM:SS" -> "14:30:45"
#              "12h" -> "2:30 PM"
# - get_next_update_time(interval: int, timezone: str) -> datetime
```

### `bot/utils/name_utils.py` — Ism Yordamchisi
```python
# Funksiyalar:
# - strip_time_tag(name: str) -> str
#   Regex: r'\s*[\[\(\{\<\|]?\d{1,2}:\d{2}(:\d{2})?[\]\)\}\>\|]?\s*$'
# - add_time_tag(name: str, time_str: str, bracket: str, prefix: str) -> str
# - validate_name_length(name: str) -> bool  # Telegram: max 64 belgi
# - extract_original_name(name: str) -> str
```

---

## ⚙️ API VA KONFIGURATSIYA

### `.env` fayli
```env
# Bot Token (BotFather dan olinadi)
BOT_TOKEN=1234567890:AAFxxx...

# Admin ID lar (vergul bilan ajratilgan)
ADMIN_IDS=123456789,987654321

# SQLite DB yo'li
DATABASE_PATH=./data/bot.db

# Log darajasi
LOG_LEVEL=INFO

# Webhook sozlamalari (agar webhook ishlatilsa)
WEBHOOK_URL=https://yourdomain.com/webhook
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8080

# Default sozlamalar
DEFAULT_TIMEZONE=Asia/Tashkent
DEFAULT_LANGUAGE=uz
DEFAULT_INTERVAL=1
```

### `config.py`
```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: List[int]
    DATABASE_PATH: str = "./data/bot.db"
    LOG_LEVEL: str = "INFO"
    DEFAULT_TIMEZONE: str = "Asia/Tashkent"
    DEFAULT_LANGUAGE: str = "uz"
    DEFAULT_INTERVAL: int = 1  # daqiqalar
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### `requirements.txt`
```
aiogram==3.7.0
aiosqlite==0.20.0
apscheduler==3.10.4
python-dotenv==1.0.0
pydantic-settings==2.2.1
pytz==2024.1
aiohttp==3.9.3
pyrogram==2.0.106      # User API uchun
tgcrypto==1.2.5        # Pyrogram kripto tezlashtiruvchi
loguru==0.7.2          # Kuchli loglash
```

---

## 🔐 XAVFSIZLIK

### Foydalanuvchi Ulanish Jarayoni (OAuth-like Flow)

```
Foydalanuvchi → /connect → Bot telefon so'radi
                         ↓
                   OTP kod yuboriladi (Telegram orqali)
                         ↓
                   Foydalanuvchi kodni botga yuboradi
                         ↓
                   Pyrogram sessiya yaratiladi
                         ↓
                   Sessiya shifrlangan holda DB ga saqlanadi
                         ↓
                   Profil yangilash huquqi beriladi
```

### Xavfsizlik Tadbirlari

| Xatar | Himoya |
|-------|--------|
| Token sizib chiqishi | `.env` + `.gitignore` |
| Sessiya o'g'irlanishi | Session string shifrlanadi (AES) |
| Flood / Spam | ThrottlingMiddleware (10 req/min) |
| Noma'lum foydalanuvchilar | DB da ro'yxatdan o'tish majburiy |
| Admin operatsiyalari | `admin_only` decorator |
| SQL Injection | Parametrlangan so'rovlar (`aiosqlite`) |
| Vaqt hujumi | Barcha operatsiyalar UTC da, ko'rsatishda timezone |

---

## 🚀 DEPLOY VA CI/CD

### Local Ishga Tushirish
```bash
# 1. Loyihani klonlash
git clone https://github.com/username/telegram-name-bot.git
cd telegram-name-bot

# 2. Virtual muhit
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# 3. Kutubxonalar o'rnatish
pip install -r requirements.txt

# 4. .env fayl yaratish
cp .env.example .env
# .env faylni to'ldiring

# 5. Database yaratish
python -c "from bot.database.models import create_tables; import asyncio; asyncio.run(create_tables())"

# 6. Botni ishga tushirish
python main.py
```

### Docker bilan Ishga Tushirish
```bash
# Build
docker build -t telegram-name-bot .

# Run
docker run -d \
  --name name-bot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  telegram-name-bot

# Docker Compose
docker-compose up -d
```

### `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data logs

CMD ["python", "main.py"]
```

---

## 🧪 TESTLAR

### Test Strategiyasi
```
tests/
├── test_name_service.py     # strip_time_tag, add_time_tag testlar
├── test_time_utils.py       # format_time, get_current_time testlar
├── test_database.py         # CRUD operatsiyalar testlar
└── test_middlewares.py      # Throttling, auth testlar
```

### Test Ishga Tushirish
```bash
pytest tests/ -v --asyncio-mode=auto
```

---

## 📈 KELAJAK REJALAR (v2.0)

| Xususiyat | Ustuvorlik | Tavsif |
|-----------|------------|--------|
| Premium reja | Yuqori | Ko'proq foydalanuvchilar uchun tezlashtirilgan yangilanish |
| Bio yangilash | O'rta | Profil bio ga ham vaqt qo'shish |
| Rasm yangilash | O'rta | Profil rasmni vaqtga qarab o'zgartirish |
| Guruh statistikasi | Past | Guruh a'zolari statistikasi |
| Web panel | O'rta | Web admin panel |
| Multi-bot | Past | Bir server — ko'p bot instansiya |
| PostgreSQL | O'rta | Katta foydalanuvchi bazasi uchun migratsiya |
| Redis Cache | O'rta | Tez-tez so'raladigan ma'lumotlarni keshlash |

---

## 📌 MUHIM ESLATMALAR

> ⚠️ **Telegram API Cheklovlari:**
> - Profil ism o'zgartirish: soatiga maksimal ~5-10 marta (Telegram cheklov qo'yishi mumkin)
> - Ism uzunligi: maksimal 64 belgi
> - Username o'zgartirib bo'lmaydi (faqat `first_name` va `last_name`)
> - Pyrogram/Telethon User API ishlatish Telegram ToS ga mos kelishi kerak

> ℹ️ **Tavsiya:**
> - Bot API `setMyName` emas, balki `edit_profile` (User API) ishlatiladi
> - Har foydalanuvchi uchun alohida APScheduler Job yaratiladi
> - Barcha vaqt hisobi UTC da saqlanadi, ko'rsatishda foydalanuvchi timezone si qo'llanadi

---

*Hujjat yaratilgan: Professional Telegram Bot Arxitektori tomonidan*  
*Versiya: 1.0.0 | O'zbek tili*