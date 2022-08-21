
from telebot.types import KeyboardButton

from .schemas import User


def reply_keyboard_columns_generator(btn_names_list: list, col=2):
    row = []
    for index, btn_name in enumerate(btn_names_list, 1):
        row += [KeyboardButton(btn_name)]
        if index % col == 0:
            yield row
            row = []
    if row:
        yield row
