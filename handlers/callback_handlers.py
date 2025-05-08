from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, FSInputFile, Message
from keyboards.callback_data import CallbackData, CelebrityData
from keyboards.reply_keyboards import kb_replay
from aiogram.fsm.context import FSMContext
from .hendlers_state import GPTStateRequests
from classes import gpt_client, ChatGPT
import os

callback_router = Router()


@callback_router.callback_query(CelebrityData.filter(F.button == 'select_celebrity'))
async def celebrity_callbacks(callback: CallbackQuery, callback_data: CallbackData, bot: Bot, state: FSMContext):
    photo_path = os.path.join('resources', 'images', callback_data.file_name + '.jpg')
    text_path = os.path.join('resources', 'prompts', callback_data.file_name + '.txt')
    buttons = ('Закончить',)
    with open(text_path, 'r', encoding='utf-8') as file:
        text = file.readline()[5:-2:] + '\nЗадай ему свой вопрос:'
    with open(text_path, 'r', encoding='utf-8') as file:
        prompt = file.read()
    photo = FSInputFile(photo_path)
    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=photo,
        caption=text,
        reply_markup=kb_replay(buttons),
    )
    await state.update_data({'chat_id': callback.from_user.id})
    await state.update_data({'prompt': prompt})
    await state.update_data(history=[])
    await state.set_state(GPTStateRequests.chatting)


@callback_router.message(GPTStateRequests.chatting)
async def chat_gpt_celebrity(message: Message, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    query_user_text = message.text
    chat_id = state_data['chat_id']
    prompt = state_data['prompt']
    history = state_data['history']
    history.append({"role": "user", "content": query_user_text})
    answer = await gpt_client.celebrity_request(prompt, history)
    history.append({"role": "assistant", "content": answer})
    await state.update_data(history=history)
    await message.bot.send_message(
        chat_id=chat_id,
        text=answer,
    )





