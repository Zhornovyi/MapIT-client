import requests
from os import environ
from json import dumps
from telebot.types import CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, Message
from src.data import Data
from src.schemas import User
from .data import AGE_GROUPS, CLASS_FORMATS, SERVER_LINK


def get_user(message: Message) -> User:
    user_chat_id = message.chat.id
    user = User.objects.filter(chat_id=user_chat_id)
    if len(user) == 0:
        
        username = message.chat.username if message.chat.username is not None else "No Nickname"
        name = message.chat.first_name if message.chat.first_name is not None else "No Name"
        surname = message.chat.last_name if message.chat.last_name is not None else "No Surname"
        
        user = User(
            chat_id=user_chat_id,
            name=name,
            surname=surname,
            username=username,
            email= "No email",
            registered = False,
        )
        return user
    else:
        return user[0]
class UserSection:
    START_BUTTON = "Почати тест"

    def __init__(self, data: Data):
        self.data = data
        self.bot = data.bot

    def send_start_menu(self, user: User):
        btn_pass_testing = KeyboardButton(text=self.START_BUTTON)
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(btn_pass_testing)
        self.bot.send_message(
            user.chat_id,
            text="Супер! Попереду міні-тест з 8 простих питань, які допоможуть обрати напрям навчання",
            reply_markup=markup
        )

    def send_result_menu(self, user: User, call: CallbackQuery = None):
        text_message = get_user_topics_response(user)
        markup = self.form_result_menu_markup()
        if call is None:
            self.bot.send_message(chat_id=user.chat_id, text=text_message, reply_markup=markup)
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
    
def get_user_topics_response(user: User):
    params = dumps(convert_request_form_into_params(user.request_form))
    resp = requests.request(method='get', 
                            url=f"{SERVER_LINK}/courses_topics/", 
                            data=params)
    if resp.status_code == 200:
        topics = resp.json()['topics']
        result = "За вашим запитом ми рекомендуємо вам наступні теми курсів. Щоб отримати повну підбірку оплатіть замовлення. \n"
        if topics:
            for topic in topics:
                result+=f"{topic}\n"
        else:
            result = "Нажаль за вашим запитом не знайдено жодного курсу"
    else:
        result = "Можливо сталася помилка. Зверніться до адміністатора @OfficeMapIT"
    return result

def convert_request_form_into_params(form:dict) -> dict:
    params = {
        'age_group': AGE_GROUPS.index(form['child_age'])+1,
        'frmt_online': True if form['format'] in [CLASS_FORMATS[0], CLASS_FORMATS[2]] else False,
        'frmt_offline': True if form['format'] in [CLASS_FORMATS[1], CLASS_FORMATS[2]] else False,
        'city': None,
        'classes_type': True if form['type'] == 'Індивідуальні' else False,
        'thinking': True if form['thinking'] == 'Логічний' else False,
        'experience_it': True if ['experience_it'] == 'Maє' else False,
        'experience_online': True if ['expeience_online'] == "Maє" else False,
    }    
    if 'city' in form:
        params['city']= form['city'] 
    
    return params