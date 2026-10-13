import sys
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN, ADMIN_IDS
from bot import database
from bot.handlers import register_all_handlers

import os
from aiohttp import web

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("AcademyBroadcastBot")


async def start_health_server(port: int):
    """Bulutli serverlar (Render, Koyeb) uchun portni ochiq saqlash web serveri."""
    app = web.Application()

    async def handle_ping(request):
        return web.Response(text="Academy Broadcast Bot 24/7 is running!")

    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Cloud health-check web server {port}-portda ishga tushdi.")


async def main():
    """Botning asosiy ishga tushish funksiyasi."""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "\n❌ XATOLIK: BOT_TOKEN ko'rsatilmagan!\n"
            "Iltimos, .env faylini oching va @BotFather orqali olingan tokenni kiriting.\n"
            "Misol: BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz\n"
        )
        return

    if not ADMIN_IDS:
        logger.warning(
            "\n⚠️ DIQQAT: ADMIN_IDS ko'rsatilmagan!\n"
            "Botga faqat adminlar post tarqata oladi. .env fayliga Telegram ID ingizni yozing.\n"
            "O'z ID ingizni bilish uchun @userinfobot ga yozishingiz mumkin.\n"
        )

    # 1. Ma'lumotlar bazasini ishga tushirish
    logger.info("Ma'lumotlar bazasi initsializatsiya qilinmoqda...")
    await database.init_db()

    # Bulutli bepul serverlar uchun (agar PORT mavjud bo'lsa)
    port_env = os.getenv("PORT")
    if port_env and port_env.isdigit():
        await start_health_server(int(port_env))

    # 2. Bot va Dispatcher obyektlarini yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # 3. Routerlarni ro'yxatdan o'tkazish
    register_all_handlers(dp)

    # 4. Bot ishga tushganda adminlarga bildirishnoma yuborish
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text="🚀 <b>Akademiya Xabar Tarqatuvchi Boti muvaffaqiyatli ishga tushdi!</b>",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.debug(f"Adminga ({admin_id}) start xabarini yuborib bo'lmadi: {e}")

    # 5. Polling orqali yangilanishlarni qabul qilish
    # DIQQAT: 'my_chat_member' yangilanishini qabul qilish uchun allowed_updates ga kiritish shart!
    allowed_updates = ["message", "callback_query", "my_chat_member"]

    logger.info("Bot ishga tushdi va xabarlarni tinglamoqda...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=allowed_updates)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
