import logging, os
import configparser
from src.quiz import send_welcome_message_and_start_quiz, start_testing_quiz
from src.data import Data
from src.user import UserSection, get_user
from src.schemas import InterfaceMessages
from telebot import TeleBot, logger

logger.setLevel(logging.INFO)
logger.info("Initializing settings")
config = configparser.ConfigParser()
config.read("Settings.ini")
logger.info("Settings read")

API_TOKEN = os.environ.get("TOKEN", False) if os.environ.get("TOKEN", False) else config["TG"]["token"]
CONNECTION_STRING = os.environ.get("DB", False) if os.environ.get("DB", False) else config["Mongo"]["db"]

bot = TeleBot(API_TOKEN, parse_mode="HTML")
data = Data(conn_string=CONNECTION_STRING, bot=bot)

logger.info("Connected to db")

user_section = UserSection(data=data)

@bot.message_handler(commands=["start"])
def start_bot(message):
    user = get_user(message)
    try:
        if not user.registered:
            send_welcome_message_and_start_quiz(user, bot, user_section)
        else:
            user_section.send_start_menu(user=user)
    except Exception as e:
       logger.error(f"Exception during start - {e}")

@bot.message_handler(commands=["info"])
def get_contacts(message):
    user = get_user(message)
    msg  = InterfaceMessages.objects.filter(name="InterfaceMessages").first().info_text
    bot.send_message(chat_id = user.chat_id, 
                     text=msg)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user = get_user(call.message)
    bot.clear_step_handler_by_chat_id(user.chat_id)
    section = call.data.split(";")[0]

    try:
        if section == "User":
            user_section.process_callback(call=call, user=user)

    except Exception as e:
        logger.error(f"Exception during {section}.{call.data.split(';')[1]} btn tap - {e}")


@bot.message_handler(content_types=["text"])
def handle_text_buttons(message):
    user = get_user(message)
    message_text = message.text
    try:
        if message_text == user_section.START_BUTTON:
            start_testing_quiz(user=user, bot=bot, final_func=user_section.send_result_menu)
        else:
            pass  # answer user that it was invalid input (in utils.py maybe)

    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    bot.polling(True)