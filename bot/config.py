import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()

raw_admins = os.getenv("ADMIN_IDS", "").strip()
ADMIN_IDS: List[int] = []
if raw_admins:
    for admin_id in raw_admins.split(","):
        cleaned = admin_id.strip()
        if cleaned.isdigit():
            ADMIN_IDS.append(int(cleaned))

DB_PATH: str = os.getenv("DB_PATH", "database.sqlite3").strip()


def is_admin(user_id: int) -> bool:
    """Tekshirish: foydalanuvchi adminlar ro'yxatida bormi?"""
    return user_id in ADMIN_IDS
