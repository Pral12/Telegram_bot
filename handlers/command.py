from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from keyboards import kb_replay, ikb_celebrity
import os
from classes import gpt_client, ChatGPT
from .hendlers_state import GPTStateRequests

command_router = Router()


@command_router.message(GPTStateRequests.waiting_for_request)
async def wait_for_gpt_handler(message: Message, state: FSMContext, bot: Bot):
    if message.text.strip() == 'Закончить' or message.text.strip() == '/start':
        await message.answer(
            text='Введите команду "/start" или нажмите повторно кнопку "Закончить"',
        )
        await state.clear()
    else:
        await bot.send_chat_action(
            chat_id=message.from_user.id,
            action=ChatAction.TYPING,
        )
        photo_path = os.path.join('resources', 'images', 'gpt.jpg')
        photo = FSInputFile(photo_path)
        msg_text = await gpt_client.gpt_request(message.text.strip())
        await message.answer_photo(
            photo=photo,
            caption=msg_text,
        )
    # await state.clear()

@command_router.message(F.text == "Закончить")
@command_router.message(Command('start'))
async def com_start(message: Message, state: FSMContext):
    await state.clear()
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
async def com_random(message: Message, bot: Bot):
    await bot.send_chat_action(
        chat_id=message.from_user.id,
        action=ChatAction.TYPING,
    )
    photo_path = os.path.join('resources', 'images', 'random.jpg')
    photo = FSInputFile(photo_path)
    buttons = ('Хочу еще факт', 'Закончить',)
    msg_text = await gpt_client.random_request()
    await message.answer_photo(
        photo=photo,
        caption=msg_text,
        reply_markup=kb_replay(buttons),
    )



@command_router.message(F.text == "Задать вопрос gpt")
@command_router.message(Command('gpt'))
async def com_gpt(message: Message, state: FSMContext, bot: Bot):
    await bot.send_chat_action(
        chat_id=message.from_user.id,
        action=ChatAction.TYPING,
    )
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
    await state.set_state(GPTStateRequests.waiting_for_request)


@command_router.message(Command('talk'))
async def com_talk(message: Message, state: FSMContext, bot: Bot):
    await bot.send_chat_action(
        chat_id=message.from_user.id,
        action=ChatAction.TYPING,
    )
    photo_path = os.path.join('resources', 'images', 'talk.jpg')
    text_path = os.path.join('resources', 'messages', 'talk.txt')
    photo = FSInputFile(photo_path)
    with open(text_path, 'r', encoding='UTF-8') as file:
        msg_text = file.read()
    await message.answer_photo(
        photo=photo,
        caption=msg_text,
        reply_markup=ikb_celebrity(),
    )