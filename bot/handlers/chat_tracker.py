import logging
from aiogram import Router, Bot
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus, ChatType

from bot import database
from bot.config import ADMIN_IDS

router = Router(name="chat_tracker")
logger = logging.getLogger(__name__)


@router.my_chat_member()
async def on_my_chat_member_update(event: ChatMemberUpdated, bot: Bot):
    """
    Bot guruhga yoki kanalga qo'shilganda yoki chiqarib yuborilganda
    avtomatik ravishda bazada ro'yxatga olish / yangilash.
    """
    chat = event.chat
    new_status = event.new_chat_member.status
    old_status = event.old_chat_member.status

    chat_type_str = "Kanal" if chat.type == ChatType.CHANNEL else "Guruh"

    logger.info(
        f"Chat status yangilandi: ChatID={chat.id}, Type={chat.type}, "
        f"Eski holat={old_status}, Yangi holat={new_status}"
    )

    # 1. Bot chatga qo'shildi yoki admin qilindi
    if new_status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER):
        await database.add_or_update_chat(
            chat_id=chat.id,
            chat_type=chat.type,
            title=chat.title or "Nomsiz",
            username=chat.username,
            is_active=1
        )

        admin_msg = (
            f"🔔 <b>Yangi {chat_type_str} ulandi!</b>\n\n"
            f"📌 <b>Nomi:</b> {chat.title or 'Nomsiz'}\n"
            f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
            f"📂 <b>Turi:</b> {chat.type}\n"
            f"🔗 <b>Username:</b> @{chat.username}" if chat.username else f"🔗 <b>Username:</b> Yo'q"
        )

        # Adminlarga xabar berish
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(chat_id=admin_id, text=admin_msg, parse_mode="HTML")
            except Exception as e:
                logger.warning(f"Adminga ({admin_id}) xabar yetkazib bo'lmadi: {e}")

    # 2. Bot chatdan chiqarildi yoki bloklandi
    elif new_status in (ChatMemberStatus.KICKED, ChatMemberStatus.LEFT):
        await database.set_chat_inactive(chat.id)

        admin_msg = (
            f"⚠️ <b>Bot {chat_type_str.lower()}dan chiqarildi!</b>\n\n"
            f"📌 <b>Nomi:</b> {chat.title or 'Nomsiz'}\n"
            f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
            f"<i>Ushbu chat avtomatik ravishda nofaol deb belgilandi.</i>"
        )

        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(chat_id=admin_id, text=admin_msg, parse_mode="HTML")
            except Exception as e:
                logger.warning(f"Adminga ({admin_id}) xabar yetkazib bo'lmadi: {e}")
