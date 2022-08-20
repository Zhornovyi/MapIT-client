from telebot.types import CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from src.data import Data
from src.schemas import User
from src.quiz import start_testing_quiz
from .utils import get_courses_api_response


class UserSection:
    TEXT_BUTTONS = ["Почати тест"]

    def __init__(self, data: Data):
        self.data = data
        self.bot = data.bot

    def process_text(self, text: str, user: User):
        if text == self.TEXT_BUTTONS[0]:
            start_testing_quiz(user, is_random=True)

    def send_start_menu(self, user: User):

        btn_pass_testing = KeyboardButton(text=self.TEXT_BUTTONS[0])

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(btn_pass_testing)

        self.bot.send_message(
            user.chat_id,
            text="Супер! Попереду міні-тест з 8 простих питань, які допоможуть обрати напрям навчання",
            reply_markup=markup
        )

    def send_result_menu(self, user: User, call: CallbackQuery = None):
        text_message = get_courses_api_response(user)

        markup = self.form_result_menu_markup()

        if call is None:
            self.bot.send_message(
                chat_id=user.chat_id, text=text_message, reply_markup=markup
            )
        else:
            self.send_message(call, text=text_message, reply_markup=markup)
    
    def form_result_menu_markup(self) -> InlineKeyboardMarkup:
        criteria_markup = InlineKeyboardMarkup()
        callback_data = self.form_user_callback(action="Pay")
        pay_but = InlineKeyboardButton(text="Pay", callback_data=callback_data)
        criteria_markup.add(pay_but)
        return criteria_markup
    
    def process_callback(self, call: CallbackQuery, user: User):
        action = call.data.split(";")[1]

        if action == "Pay":
            self.get_payment_menu(user, call=call)
        else:
            self.answer_wrong_action(call)

        self.bot.answer_callback_query(call.id)
    
    def answer_wrong_action(self, call: CallbackQuery):
        wrong_action_text = "Неправильний action в callback.data"
        self.bot.answer_callback_query(call.id, text=wrong_action_text)
    
    def get_payment_menu(self, user, call=None):
        self.bot.send_message(chat_id=user.chat_id, text="Меседж про спосіб оплати")
        self.bot.send_message(chat_id=user.chat_id, text="Розширена відповідь")

    def form_user_callback(self, action, user_id=""):
        return f"User;{action};{user_id};"