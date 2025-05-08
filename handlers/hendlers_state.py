from aiogram.fsm.state import State, StatesGroup


class GPTStateRequests(StatesGroup):
    waiting_for_request = State()
    choosing = State()  # Выбор персонажа
    chatting = State()  # Диалог