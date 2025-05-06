from aiogram.utils.keyboard import InlineKeyboardBuilder
from .callback_data import CelebrityData
import os

def ikb_celebrity():
    keyboard = InlineKeyboardBuilder()
    path_celebrity = os.path.join('resources', 'prompts')
    celebrity_list = [file for file in os.listdir(path_celebrity) if file.startswith('talk_')]
    buttons = []
    for file in celebrity_list:
        with open(os.path.join(path_celebrity, file), 'r', encoding='utf-8') as txt_file:
            buttons.append((txt_file.readline()[5::].split(", ")[0], file.split('.')[0]))
    for button_name, file_name in buttons:
        keyboard.button(
            text=button_name,
            callback_data=CelebrityData(
                button='select_celebrity',
                file_name=file_name,
            ),
        )
    keyboard.adjust(1)
    return keyboard.as_markup()