import aiosqlite
from typing import List, Optional, Dict, Any
from bot.config import DB_PATH


async def init_db() -> None:
    """Ma'lumotlar bazasini va kerakli jadvallarni yaratish."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER UNIQUE NOT NULL,
                chat_type TEXT NOT NULL,
                title TEXT,
                username TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS broadcast_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                target_type TEXT NOT NULL,
                total_chats INTEGER NOT NULL,
                successful_chats INTEGER NOT NULL,
                failed_chats INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def add_or_update_chat(
    chat_id: int,
    chat_type: str,
    title: Optional[str] = None,
    username: Optional[str] = None,
    is_active: int = 1
) -> None:
    """Guruh yoki kanalni bazaga qo'shish yoki holatini yangilash."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO chats (chat_id, chat_type, title, username, is_active, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(chat_id) DO UPDATE SET
                chat_type = excluded.chat_type,
                title = excluded.title,
                username = excluded.username,
                is_active = excluded.is_active,
                updated_at = CURRENT_TIMESTAMP
        """, (chat_id, chat_type, title, username, is_active))
        await db.commit()


async def set_chat_inactive(chat_id: int) -> None:
    """Bot chiqarib yuborilgan yoki xabar jo'natib bo'lmagan chatni nofaol deb belgilash."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE chats
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE chat_id = ?
        """, (chat_id,))
        await db.commit()


async def get_active_chats(filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Faol chatlarni olish.
    filter_type: 'channel', 'group' (group yoki supergroup), yoki None (barchasi)
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if filter_type == "channel":
            query = "SELECT * FROM chats WHERE is_active = 1 AND chat_type = 'channel'"
            cursor = await db.execute(query)
        elif filter_type == "group":
            query = "SELECT * FROM chats WHERE is_active = 1 AND chat_type IN ('group', 'supergroup')"
            cursor = await db.execute(query)
        else:
            query = "SELECT * FROM chats WHERE is_active = 1"
            cursor = await db.execute(query)

        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_all_chats(limit: int = 100) -> List[Dict[str, Any]]:
    """Barcha chatlarni (faol va nofaol) ro'yxatini olish."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM chats
            ORDER BY is_active DESC, updated_at DESC
            LIMIT ?
        """, (limit,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_stats() -> Dict[str, Any]:
    """Umumiy statistika ma'lumotlarini olish."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Faol kanallar
        async with db.execute("SELECT COUNT(*) FROM chats WHERE is_active = 1 AND chat_type = 'channel'") as c:
            channels_count = (await c.fetchone())[0]

        # Faol guruhlar
        async with db.execute("SELECT COUNT(*) FROM chats WHERE is_active = 1 AND chat_type IN ('group', 'supergroup')") as c:
            groups_count = (await c.fetchone())[0]

        # Nofaol chatlar
        async with db.execute("SELECT COUNT(*) FROM chats WHERE is_active = 0") as c:
            inactive_count = (await c.fetchone())[0]

        # Tarqatishlar soni
        async with db.execute("SELECT COUNT(*) FROM broadcast_logs") as c:
            broadcasts_count = (await c.fetchone())[0]

        return {
            "channels": channels_count,
            "groups": groups_count,
            "total_active": channels_count + groups_count,
            "inactive": inactive_count,
            "broadcasts": broadcasts_count,
        }


async def log_broadcast(
    admin_id: int,
    target_type: str,
    total_chats: int,
    successful_chats: int,
    failed_chats: int
) -> None:
    """Tarqatish tarixi jurnaliga yozish."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO broadcast_logs (admin_id, target_type, total_chats, successful_chats, failed_chats)
            VALUES (?, ?, ?, ?, ?)
        """, (admin_id, target_type, total_chats, successful_chats, failed_chats))
        await db.commit()
