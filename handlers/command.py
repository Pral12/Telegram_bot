from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import kb_replay
import os
from classes import gpt_client, ChatGPT

class GPTState(StatesGroup):
    waiting_for_query = State()

command_router = Router()
@command_router.message(F.text == "Закончить")
@command_router.message(Command('start'))
async def com_start(message: Message):
    photo_path = os.path.join('resources', 'images', 'main.jpg')
    text_path = os.path.join('resources', 'messages', 'main.txt')
    photo = FSInputFile(photo_path)
    buttons = ('/random', '/gpt', '/talk', '/quiz',)
    with open(text_path, 'r', encoding='UTF-8') as file:
        msg_text = file.read()
    await message.answer_photo(
        photo=photo,
        caption=msg_text,
        reply_markup=kb_replay(buttons),
    )

@command_router.message(F.text == "Хочу еще факт")
@command_router.message(Command('random'))
async def com_random(message: Message):
    photo_path = os.path.join('resources', 'images', 'random.jpg')
    photo = FSInputFile(photo_path)
    buttons = ('Хочу еще факт', 'Закончить',)
    msg_text = await gpt_client.text_request('random')
    await message.answer_photo(
        photo=photo,
        caption=msg_text,
        reply_markup=kb_replay(buttons),
    )



@command_router.message(F.text == "Задать вопрос gpt")
@command_router.message(Command('gpt'))
async def com_gpt(message: Message, state: FSMContext):
    photo_path = os.path.join('resources', 'images', 'gpt.jpg')
    text_path = os.path.join('resources', 'messages', 'gpt.txt')
    photo = FSInputFile(photo_path)
    buttons = ('Задать вопрос gpt', 'Закончить',)
    with open(text_path, 'r', encoding='UTF-8') as file:
        msg_text = file.read()
    await message.answer_photo(
        photo=photo,
        caption=msg_text,
        reply_markup=kb_replay(buttons),
    )
    await state.set_state(GPTState.waiting_for_query)

@command_router.message(GPTState.waiting_for_query)
async def process_query(message: Message, state: FSMContext):
    user_text = message.text.strip()
    msg_text = await gpt_client.text_request(user_text)
    await message.answer(
        text=msg_text,
    )
