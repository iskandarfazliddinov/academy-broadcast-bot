from aiogram import Dispatcher
from bot.handlers.chat_tracker import router as chat_tracker_router
from bot.handlers.broadcast import router as broadcast_router
from bot.handlers.admin import router as admin_router
from bot.handlers.common import router as common_router


def register_all_handlers(dp: Dispatcher) -> None:
    """Barcha routerlarni dispatcherga ro'yxatdan o'tkazish."""
    dp.include_router(chat_tracker_router)
    dp.include_router(broadcast_router)
    dp.include_router(admin_router)
    dp.include_router(common_router)
