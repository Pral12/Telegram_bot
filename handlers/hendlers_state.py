from aiogram.fsm.state import State, StatesGroup


class GPTStateRequests(StatesGroup):
    waiting_for_request = State()