from telebot.types import Message, KeyboardButton, CallbackQuery
from telebot import TeleBot

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


def delete_message(bot: TeleBot, call: CallbackQuery):
    chat_id = call.message.chat_id
    message_id = call.message.message_id

    try:
        bot.delete_message(chat_id, message_id)

    except:
        bot.answer_callback_query(call.id, text="Щоб продовжити натискай на /start")

def get_courses_api_response(user: User):
    return f"За вашим запитом ми отримали такі відповіді {user.request_form}"