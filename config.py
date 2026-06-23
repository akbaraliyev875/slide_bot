"""
Loyiha konfiguratsiyasi — .env fayldan o'zgaruvchilarni yuklaydi.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union


# Loyihaning ildiz papkasi
BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Bot konfiguratsiya sozlamalari."""

    # — Bot —
    BOT_TOKEN: str

    # — Admin —
    ADMIN_IDS: List[int] = []

    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        if isinstance(v, int):
            return [v]
        return v

    # — Pyrogram (User API) —
    API_ID: int = 0
    API_HASH: str = ""

    # — Database —
    DATABASE_PATH: str = "./data/bot.db"

    # — Logging —
    LOG_LEVEL: str = "INFO"

    # — Defaultlar —
    DEFAULT_TIMEZONE: str = "Asia/Tashkent"
    DEFAULT_LANGUAGE: str = "uz"

    @property
    def DEFAULT_INTERVAL(self) -> int:
        return 1

    @property
    def db_path(self) -> Path:
        """Database ning to'liq yo'li."""
        path = Path(self.DATABASE_PATH)
        if not path.is_absolute():
            path = BASE_DIR / path
        # data papkasini yaratish
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def sessions_dir(self) -> Path:
        """Pyrogram sessiya fayllari uchun papka."""
        path = BASE_DIR / "sessions"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def logs_dir(self) -> Path:
        """Log fayllari uchun papka."""
        path = BASE_DIR / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instansiyasi
settings = Settings()
