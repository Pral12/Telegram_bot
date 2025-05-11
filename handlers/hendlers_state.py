from aiogram.fsm.state import State, StatesGroup


class GPTStateRequests(StatesGroup):
    waiting_for_request = State()
    choosing = State()
    chatting = State()
    quiz_game = State()