# 🤖 Telegram Profile Name Auto-Updater Bot

Telegram foydalanuvchilarining profil ismiga avtomatik ravishda joriy vaqtni qo'shib turuvchi bot.

```
Ismoil  →  Ismoil [14:00]  →  Ismoil [15:00]
```

## 📦 Texnologiyalar

| Texnologiya | Versiya | Maqsad |
|-------------|---------|--------|
| Python | 3.11+ | Asosiy dasturlash tili |
| Aiogram | 3.7+ | Telegram Bot Framework |
| SQLite | 3.x | Ma'lumotlar bazasi |
| APScheduler | 3.10+ | Vazifalar rejalashtiruvchi |
| Pyrogram | 2.0+ | User API (profil yangilash) |

## 🚀 Ishga Tushirish

### 1. Virtual muhit yaratish
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Kutubxonalar o'rnatish
```bash
pip install -r requirements.txt
```

### 3. `.env` fayl yaratish
```bash
cp .env.example .env
```
`.env` fayldagi qiymatlarni to'ldiring:
- `BOT_TOKEN` — @BotFather dan oling
- `API_ID` va `API_HASH` — https://my.telegram.org dan oling
- `ADMIN_IDS` — Telegram ID ingiz

### 4. Botni ishga tushirish
```bash
python main.py
```

## 📋 Buyruqlar

### Asosiy
- `/start` — Botni ishga tushirish
- `/connect` — Profilni ulash
- `/disconnect` — Profilni uzish
- `/status` — Bot holati
- `/help` — Yordam

### Sozlamalar
- `/settings` — Sozlamalar menyusi
- `/timezone` — Vaqt mintaqasi
- `/format` — Vaqt formati (HH:MM, HH:MM:SS, 12h)
- `/interval` — Yangilanish oralig'i
- `/prefix` — Matn prefiksi
- `/language` — Til (uz/ru/en)

### Statistika
- `/stats` — Shaxsiy statistika
- `/history` — Yangilanish tarixi
- `/uptime` — Bot ishlash vaqti

### Admin
- `/admin` — Admin paneli
- `/broadcast` — Ommaviy xabar
- `/ban [id] [sabab]` — Bloklash
- `/unban [id]` — Blokni ochish
- `/logs` — Tizim jurnali

## 🐳 Docker

```bash
docker-compose up -d
```

## 📄 Litsenziya

MIT
