import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from bot import database
from bot.config import is_admin
from bot.keyboards import admin_main_kb

router = Router(name="admin")
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Start komandasi handleri."""
    user_id = message.from_user.id

    if is_admin(user_id):
        stats = await database.get_stats()
        text = (
            f"Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
            "🎓 <b>Akademiya Xabar Tarqatuvchi Boti</b> admin paneliga xush kelibsiz.\n\n"
            f"📊 <b>Hozirgi holat:</b>\n"
            f"• Faol kanallar: <b>{stats['channels']}</b> ta\n"
            f"• Faol guruhlar: <b>{stats['groups']}</b> ta\n"
            f"• Jami manzillar: <b>{stats['total_active']}</b> ta\n\n"
            "Yangi xabar, reklama yoki videoni barcha kanallarga yuborish uchun "
            "quyidagi <b>'📢 Yangilik tarqatish'</b> tugmasini bosing."
        )
        await message.answer(text, reply_markup=admin_main_kb(), parse_mode="HTML")
    else:
        text = (
            f"Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
            "🎓 Bu <b>Akademiya reklama va yangiliklarini tarqatish boti</b>.\n\n"
            "📌 <b>Botdan foydalanish tartibi:</b>\n"
            "1. Botni o'zingizning Telegram kanalingizga <b>Administrator</b> qilib qo'shing "
            "(<i>Xabarlarni joylashtirish</i> ruxsati bilan).\n"
            "2. Yoki o'z guruhingizga a'zo/admin qilib qo'shing.\n\n"
            "Shunda akademiya tomonidan e'lon qilinadigan eng so'nggi yangiliklar, "
            "foydali postlar va chegirmalar avtomatik ravishda kanalingiz/guruhingizga yetib boradi."
        )
        await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📊 Statistika")
@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Ulangan chatlar va tarqatishlar statistikasi."""
    if not is_admin(message.from_user.id):
        return

    stats = await database.get_stats()
    text = (
        "📊 <b>Bot Statistikasi:</b>\n\n"
        f"📢 Faol kanallar: <b>{stats['channels']}</b> ta\n"
        f"👥 Faol guruhlar: <b>{stats['groups']}</b> ta\n"
        f"🌐 Jami faol chatlar: <b>{stats['total_active']}</b> ta\n"
        f"🚫 Chiqarib yuborilgan/Nofaol: <b>{stats['inactive']}</b> ta\n"
        f"🚀 Jami o'tkazilgan tarqatishlar: <b>{stats['broadcasts']}</b> ta\n"
    )
    await message.answer(text, reply_markup=admin_main_kb(), parse_mode="HTML")


@router.message(F.text == "📋 Guruh va kanallar")
@router.message(Command("chats"))
async def cmd_chats(message: Message):
    """Ulangan barcha guruh va kanallar ro'yxati."""
    if not is_admin(message.from_user.id):
        return

    chats = await database.get_active_chats()

    if not chats:
        await message.answer(
            "📋 Hozirda birorta ham faol kanal yoki guruh ulanmagan.\n"
            "Botni kanal/guruhingizga qo'shing.",
            reply_markup=admin_main_kb()
        )
        return

    channels = [c for c in chats if c["chat_type"] == "channel"]
    groups = [c for c in chats if c["chat_type"] in ("group", "supergroup")]

    lines = ["📋 <b>Ulangan faol chatlar ro'yxati:</b>\n"]

    if channels:
        lines.append(f"📢 <b>Kanallar ({len(channels)} ta):</b>")
        for i, ch in enumerate(channels, 1):
            user_part = f" (@{ch['username']})" if ch.get("username") else ""
            lines.append(f"{i}. <b>{ch.get('title') or 'Nomsiz'}</b>{user_part} [<code>{ch['chat_id']}</code>]")
        lines.append("")

    if groups:
        lines.append(f"👥 <b>Guruhlar ({len(groups)} ta):</b>")
        for i, gr in enumerate(groups, 1):
            user_part = f" (@{gr['username']})" if gr.get("username") else ""
            lines.append(f"{i}. <b>{gr.get('title') or 'Nomsiz'}</b>{user_part} [<code>{gr['chat_id']}</code>]")

    response_text = "\n".join(lines)

    # Agar ro'yxat juda uzun bo'lsa, Telegram 4096 belgi limitini hisobga olamiz
    if len(response_text) > 4000:
        parts = [response_text[i:i + 4000] for i in range(0, len(response_text), 4000)]
        for part in parts:
            await message.answer(part, parse_mode="HTML")
    else:
        await message.answer(response_text, reply_markup=admin_main_kb(), parse_mode="HTML")


@router.message(F.text == "ℹ️ Qo'llanma")
@router.message(Command("help"))
async def cmd_help(message: Message):
    """Botdan to'g'ri foydalanish bo'yicha qo'llanma."""
    if not is_admin(message.from_user.id):
        return

    text = (
        "ℹ️ <b>Botdan foydalanish bo'yicha qo'llanma:</b>\n\n"
        "1️⃣ <b>Kanalga ulash:</b>\n"
        "• Telegram kanalingiz sozlamalariga kiring -> 'Administrators' -> 'Add Administrator'.\n"
        "• Bot username'ini qidirib toping va administrator qiling.\n"
        "• <i>'Post Messages' (Xabarlarni joylashtirish)</i> huquqi yoqilganligiga ishonch hosil qiling.\n"
        "• Bot avtomatik ravishda kanalni ro'yxatga oladi va sizga bildirishnoma keladi.\n\n"
        "2️⃣ <b>Guruhga ulash:</b>\n"
        "• Guruhingizga botni a'zo yoki administrator sifatida qo'shing.\n"
        "• Bot guruhga qo'shilishi bilanoq uni bazaga kiritadi.\n\n"
        "3️⃣ <b>Xabar tarqatish:</b>\n"
        "• <b>'📢 Yangilik tarqatish'</b> tugmasini bosing.\n"
        "• Postni yuboring (Oddiy matn, rasm + izoh, reklama videosi, inline tugmali xabar yoki boshqa kanaldan forward xabar).\n"
        "• Tarqatish manzilini tanlang (Barchasiga, Faqat kanallarga yoki Faqat guruhlarga).\n"
        "• Bot xabarni barcha manzillarga tez va xavfsiz yetkazib beradi hamda hisobot taqdim etadi."
    )
    await message.answer(text, reply_markup=admin_main_kb(), parse_mode="HTML")
