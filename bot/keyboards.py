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
        [KeyboardButton(text="ℹ️ Qo'llanma")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


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
