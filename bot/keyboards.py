from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def admin_main_kb() -> ReplyKeyboardMarkup:
    """Admin asosiy menyusi."""
    kb = [
        [KeyboardButton(text="📢 Yangilik tarqatish")],
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="📋 Guruh va kanallar")],
        [KeyboardButton(text="🌐 Akademiya haqida"), KeyboardButton(text="📍 Lokatsiya")],
        [KeyboardButton(text="ℹ️ Qo'llanma")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def user_main_kb() -> ReplyKeyboardMarkup:
    """Oddiy foydalanuvchilar menyusi."""
    kb = [
        [KeyboardButton(text="🌐 Akademiya haqida"), KeyboardButton(text="📍 Lokatsiya")],
        [KeyboardButton(text="ℹ️ Botdan foydalanish")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def academy_links_inline_kb() -> InlineKeyboardMarkup:
    """Akademiya saytlari va ijtimoiy tarmoqlari inline tugmalari."""
    kb = [
        [
            InlineKeyboardButton(text="🌐 Rasmiy sayt", url="https://tourism-academy.uz"),
            InlineKeyboardButton(text="🎓 Online platforma", url="https://tourism-edu.uz")
        ],
        [
            InlineKeyboardButton(text="✈️ Telegram", url="https://t.me/ita_samarkand"),
            InlineKeyboardButton(text="📸 Instagram", url="https://www.instagram.com/ita_samarkand")
        ],
        [
            InlineKeyboardButton(
                text="📘 Facebook",
                url="https://www.facebook.com/people/Xalqaro-Turizm-Akademiyasi-Samarqand-kampusi/61587006718732/"
            )
        ],
        [
            InlineKeyboardButton(
                text="📍 Google Xarita (Lokatsiya)",
                url="https://www.google.com/maps?q=39.64543000691366,66.95740956008511"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def cancel_kb() -> ReplyKeyboardMarkup:
    """Amalni bekor qilish klaviaturasi."""
    kb = [
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def broadcast_target_inline_kb(
    channels_count: int = 0,
    groups_count: int = 0
) -> InlineKeyboardMarkup:
    """Tarqatish manzilini tanlash uchun inline tugmalar."""
    total = channels_count + groups_count
    kb = [
        [
            InlineKeyboardButton(
                text=f"🚀 Barchasiga ({total} ta)",
                callback_data="send:all"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"📢 Kanallarga ({channels_count} ta)",
                callback_data="send:channel"
            ),
            InlineKeyboardButton(
                text=f"👥 Guruhlarga ({groups_count} ta)",
                callback_data="send:group"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Bekor qilish",
                callback_data="send:cancel"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
