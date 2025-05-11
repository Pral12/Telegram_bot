from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
import os
import misc
from handlers import main_router

bot = Bot(
    token=os.getenv('BOT_TOKEN'),
    default=DefaultBotProperties(
        parse_mode=ParseMode.MARKDOWN,
    ),
)
dp = Dispatcher()


async def start_bot():
    """
        Функция для запуска бота. Здесь регистрируются хуки при старте и остановке,
        подключаются роутеры с обработчиками и начинается опрос серверов Telegram.
        """
    dp.startup.register(misc.on_start)
    dp.shutdown.register(misc.on_shutdown)
    dp.include_router(main_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        pass
