from aiogram import Router
from .command import command_router
from .callback_handlers import callback_router
from .quiz_game import quiz_router


main_router = Router()
main_router.include_routers(
    command_router,
    callback_router,
    quiz_router
)


__all__ = [
    'main_router',
]