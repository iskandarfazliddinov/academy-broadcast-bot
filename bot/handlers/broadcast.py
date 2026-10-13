import asyncio
import logging
from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import (
    TelegramRetryAfter,
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramAPIError
)

from bot import database
from bot.config import is_admin
from bot.states import BroadcastState
from bot.keyboards import (
    admin_main_kb,
    cancel_kb,
    broadcast_target_inline_kb
)

router = Router(name="broadcast")
logger = logging.getLogger(__name__)


@router.message(F.text == "📢 Yangilik tarqatish")
@router.message(F.text == "/broadcast")
async def cmd_start_broadcast(message: Message, state: FSMContext):
    """Tarqatish jarayonini boshlash."""
    if not is_admin(message.from_user.id):
        await message.answer("Sizda ushbu amalni bajarish uchun ruxsat yo'q.")
        return

    stats = await database.get_stats()
    total_active = stats["total_active"]

    if total_active == 0:
        await message.answer(
            "⚠️ <b>Hozircha hech qanday guruh yoki kanal ulanmagan!</b>\n\n"
            "Botni o'zingizning kanalingizga (Admin qilib) yoki guruhingizga qo'shing. "
            "Shundan so'ng bot avtomatik ravishda ularni ro'yxatga oladi.",
            parse_mode="HTML"
        )
        return

    await state.set_state(BroadcastState.waiting_for_message)
    await message.answer(
        "📝 <b>Tarqatmoqchi bo'lgan xabaringizni yuboring:</b>\n\n"
        "<i>Bu matn, rasm, video, audio, hujjat yoki bir nechta tugmali post bo'lishi mumkin.\n"
        "Xabarni bekor qilish uchun '❌ Bekor qilish' tugmasini bosing.</i>",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(BroadcastState.waiting_for_message, F.text == "❌ Bekor qilish")
@router.message(BroadcastState.waiting_for_message, F.text == "/cancel")
async def cancel_broadcast(message: Message, state: FSMContext):
    """Tarqatishni bekor qilish."""
    await state.clear()
    await message.answer(
        "❌ Xabar tarqatish bekor qilindi.",
        reply_markup=admin_main_kb()
    )


@router.message(BroadcastState.waiting_for_message)
async def process_broadcast_content(message: Message, state: FSMContext, bot: Bot):
    """Admin yuborgan xabarni qabul qilish va tasdiqlash uchun ko'rsatish."""
    if not is_admin(message.from_user.id):
        return

    # Xabar ma'lumotlarini saqlab qolamiz
    await state.update_data(
        from_chat_id=message.chat.id,
        message_id=message.message_id
    )
    await state.set_state(BroadcastState.confirm_broadcast)

    stats = await database.get_stats()
    channels_count = stats["channels"]
    groups_count = stats["groups"]

    await message.answer(
        "👆 <b>Yuqoridagi xabar barcha ulangan guruh/kanallarga yuboriladi.</b>\n\n"
        "Qayerlarga tarqatmoqchisiz? Quyidagi tugmalardan birini tanlang:",
        reply_markup=broadcast_target_inline_kb(channels_count, groups_count),
        parse_mode="HTML"
    )


@router.callback_query(BroadcastState.confirm_broadcast, F.data.startswith("send:"))
async def process_broadcast_confirmation(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Tarqatish manzilini tanlash va xabarlarni jo'natish."""
    action = callback.data.split(":")[1]

    if action == "cancel":
        await state.clear()
        await callback.message.edit_text("❌ Tarqatish bekor qilindi.")
        await callback.message.answer("Asosiy menyu:", reply_markup=admin_main_kb())
        await callback.answer()
        return

    data = await state.get_data()
    from_chat_id = data.get("from_chat_id")
    message_id = data.get("message_id")

    if not from_chat_id or not message_id:
        await callback.answer("Xatolik: Xabar topilmadi!", show_alert=True)
        await state.clear()
        return

    target_filter = None
    if action == "channel":
        target_filter = "channel"
    elif action == "group":
        target_filter = "group"

    chats = await database.get_active_chats(filter_type=target_filter)

    if not chats:
        await callback.answer("Tanlangan turdagi faol chatlar topilmadi!", show_alert=True)
        await state.clear()
        return

    await callback.answer()
    status_msg = await callback.message.edit_text(
        f"⏳ <b>Xabar tarqatilmoqda...</b>\n"
        f"Jami manzil: {len(chats)} ta\n"
        f"<i>Iltimos, jarayon tugashini kuting...</i>",
        parse_mode="HTML"
    )

    success_count = 0
    failed_count = 0

    for item in chats:
        chat_id = item["chat_id"]
        try:
            # Xabarni barcha format va tugmalari bilan nusxalash
            await bot.copy_message(
                chat_id=chat_id,
                from_chat_id=from_chat_id,
                message_id=message_id
            )
            success_count += 1
        except TelegramRetryAfter as e:
            logger.warning(f"Telegram flood limit: {e.retry_after} soniya kutilmoqda...")
            await asyncio.sleep(e.retry_after)
            try:
                await bot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=from_chat_id,
                    message_id=message_id
                )
                success_count += 1
            except Exception as retry_err:
                logger.error(f"Qayta urinishda xatolik ({chat_id}): {retry_err}")
                failed_count += 1
        except (TelegramForbiddenError, TelegramBadRequest) as e:
            logger.warning(f"Chatga yuborib bo'lmadi ({chat_id}): {e}")
            # Bot chiqarilgan yoki ruxsat yo'q bo'lsa, chatni nofaol qilamiz
            await database.set_chat_inactive(chat_id)
            failed_count += 1
        except TelegramAPIError as e:
            logger.error(f"Telegram API xatosi ({chat_id}): {e}")
            failed_count += 1
        except Exception as e:
            logger.error(f"Noma'lum xatolik ({chat_id}): {e}")
            failed_count += 1

        # Telegram limitlariga tushib qolmaslik uchun qisqa tanaffus
        await asyncio.sleep(0.05)

    # Natijani bazaga yozish
    await database.log_broadcast(
        admin_id=callback.from_user.id,
        target_type=action,
        total_chats=len(chats),
        successful_chats=success_count,
        failed_chats=failed_count
    )

    await state.clear()

    report_text = (
        "✅ <b>Xabar muvaffaqiyatli tarqatildi!</b>\n\n"
        f"📊 <b>Natijalar:</b>\n"
        f"• Tanlangan maqsad: <code>{action.upper()}</code>\n"
        f"• Jami chatlar: <b>{len(chats)}</b> ta\n"
        f"• Muvaffaqiyatli yetkazildi: <b>{success_count}</b> ta\n"
        f"• Yetib bormadi (xatolik): <b>{failed_count}</b> ta\n\n"
        "💡 <i>Eslatma: Bot chiqarib yuborilgan yoki yozish ruxsati bo'lmagan chatlar "
        "avtomatik ravishda nofaol deb belgilandi.</i>"
    )

    try:
        await status_msg.edit_text(report_text, parse_mode="HTML")
    except Exception:
        await callback.message.answer(report_text, parse_mode="HTML")

    await callback.message.answer("Asosiy menyu:", reply_markup=admin_main_kb())
