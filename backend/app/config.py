import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_SQLITE_DB = BASE_DIR / "situado_db.sqlite3"
DEFAULT_SQLITE_URL = f"sqlite:///{DEFAULT_SQLITE_DB.as_posix()}"
DATABASE_URL = os.getenv("DATABASE_URL") or DEFAULT_SQLITE_URL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
APP_TITLE = os.getenv("APP_TITLE", "Situado de Puerto Jack e IP")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
