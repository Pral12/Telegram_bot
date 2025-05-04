from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command

from aiogram.utils.keyboard import ReplyKeyboardBuilder

import asyncio
import os


bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()


@dp.message(Command('start'))
async def com_start(message: Message):
    keyboard = ReplyKeyboardBuilder()

    keyboard.button(
        text='/start',
    )
    keyboard.button(
        text='/help',
    )
    keyboard.button(
        text='Phone',
        request_contact=True,
    )
    await message.answer(
        text=f'Доброго времени суток, {message.from_user.full_name}!\nЯ готов к работе.',
        reply_markup=keyboard.as_markup(),
    )


@dp.message(Command('help'))
async def com_help(message: Message):
    await message.answer(
        text='Здесь будет справка по боту',
    )

@dp.message(F.text.lower() == 'phone')
async def com_help(message: Message):
    await message.answer(
        text='Отправь телефон в формате +71234567890',
    )


async def start_bot():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start_bot())
