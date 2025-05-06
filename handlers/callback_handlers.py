from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, FSInputFile
from keyboards.callback_data import CallbackData, CelebrityData
from keyboards.reply_keyboards import kb_replay
import os


callback_router = Router()


@callback_router.callback_query(CelebrityData.filter(F.button == 'select_celebrity'))
async def celebrity_callbacks(callback: CallbackQuery, callback_data: CallbackData, bot: Bot):
    photo_path = os.path.join('resources', 'images', callback_data.file_name + '.jpg')
    text_path = os.path.join('resources', 'prompts', callback_data.file_name + '.txt')
    buttons = ('Задать вопрос', 'Закончить',)
    with open(text_path, 'r', encoding='utf-8') as file:
        prompt = file.read()
    photo = FSInputFile(photo_path)
    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=photo,
        caption=prompt,
        reply_markup=kb_replay(buttons),
    )