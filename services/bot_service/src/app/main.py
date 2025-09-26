import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.handlers import router as main_router
from app.core.config import settings

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(main_router)

    print("Starting Telegram Bot Service...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())