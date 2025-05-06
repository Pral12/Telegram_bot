from aiogram import Router
from .command import command_router
from .callback_handlers import callback_router


main_router = Router()
main_router.include_routers(
    command_router,
    callback_router,
)


__all__ = [
    'main_router',
]