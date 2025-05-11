from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from keyboards import kb_replay, ikb_celebrity
import os
from classes import gpt_client, ChatGPT
from .hendlers_state import GPTStateRequests
from .quiz_game import QuizGame, register_quiz_handlers



command_router = Router()


@command_router.message(GPTStateRequests.waiting_for_request)
async def wait_for_gpt_handler(message: Message, state: FSMContext, bot: Bot):
    ''' Обрабатывает текст от пользователя, когда он находится в состоянии waiting_for_request.
        Если приходит "Закончить" или /start, состояние сбрасывается.
        В противном случае отправляется запрос к GPT и результат показывается с картинкой.'''
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
    '''Срабатывает на команду /start или кнопку «Закончить».
        Сбрасывает текущее состояние FSM.
        Отправляет приветственное фото и текст + клавиатуру с командами.'''
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
    '''Запрашивает случайный факт через gpt_client.random_request().
        Отправляет фото и текст с фактом + две кнопки.'''
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
    '''Переводит пользователя в состояние ожидания запроса к GPT.
        Показывает инструкцию и клавиатуру.'''
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
    '''Предназначен для "разговора с известностью".
        Отправляет фото и инлайн-клавиатуру с выбором персонажа (ikb_celebrity()).'''
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


@command_router.message(Command('quiz'))
async def com_quiz(message: Message, state: FSMContext, bot: Bot):
    '''Начинает игру-викторину.
    Создаёт экземпляр QuizGame, регистрирует обработчики и запускает игру.'''
    quiz_game = QuizGame(bot)
    register_quiz_handlers(command_router, quiz_game)
    await bot.send_chat_action(
        chat_id=message.from_user.id,
        action=ChatAction.TYPING,
    )
    photo_path = os.path.join('resources', 'images', 'quiz.jpg')
    text_path = os.path.join('resources', 'messages', 'quiz.txt')
    photo = FSInputFile(photo_path)
    with open(text_path, 'r', encoding='UTF-8') as file:
        msg_text = file.read()
    await message.answer_photo(
        photo=photo,
        caption=msg_text,
    )
    await quiz_game.start_quiz(message, state)