from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.config import is_admin
from bot.keyboards import admin_main_kb

router = Router(name="common")


@router.message(F.text == "❌ Bekor qilish")
@router.message(F.text == "/cancel")
async def cmd_cancel_general(message: Message, state: FSMContext):
    """Har qanday jarayonni bekor qilish."""
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()

    if is_admin(message.from_user.id):
        await message.answer("Barcha amallar bekor qilindi.", reply_markup=admin_main_kb())
    else:
        await message.answer("Amal bekor qilindi.")
