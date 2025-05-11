from  aiogram.utils.keyboard import ReplyKeyboardBuilder


def kb_replay(buttons):
    '''принимает список строк (например: ('/start', '/quiz', '/help')) и
     создаёт обычную клавиатуру с этими кнопками.'''

    keyboard = ReplyKeyboardBuilder()
    for button in buttons:
        keyboard.button(
            text=button,
        )
    return keyboard.as_markup(
        resize_keyboard=True,
        input_field_placeholder='Выберите действие...',
    )
