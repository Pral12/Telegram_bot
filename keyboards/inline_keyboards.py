from aiogram.utils.keyboard import InlineKeyboardBuilder
from .callback_data import CelebrityData
import os

def ikb_celebrity():
    '''динамически создаёт инлайн-клавиатуру с кнопками для выбора знаменитости,
    с которой пользователь хочет "поговорить".
    Каждая кнопка:
    Отображает имя персонажа (например, «Альберт Эйнштейн»).
    При нажатии отправляет callback с именем файла (talk_einstein и т.д.),
    чтобы бот мог загрузить соответствующий промпт и изображение.'''

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