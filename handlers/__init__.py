from aiogram import Router
from .command import command_router

main_router = Router()
main_router.include_router(command_router)

__all__ = ['main_router']