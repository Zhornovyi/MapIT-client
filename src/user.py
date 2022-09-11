import requests
from json import dumps
from telebot.types import CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, Message, LabeledPrice
from src.data import Data
from src.schemas import User, InterfaceMessages
from .data import AGE_GROUPS, CLASS_FORMATS, SERVER_LINK, API_TOKEN, PAY_TOKEN

prices = [LabeledPrice(label='Отримати курси', amount=120_00)]

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
            text=InterfaceMessages.objects.filter(name="InterfaceMessages").first().start_menu_text,
            reply_markup=markup
        )

    def send_free_result_answear(self, user: User, call: CallbackQuery = None):
        text_message, succeed = get_user_topics_response(user)
        self.bot.send_message(user.chat_id, text_message)
        if succeed:
            self.bot.send_invoice(
                        user.chat_id,
                        'Отримати список шкіл з контактами',
                        "Щоб отримати список шкіл за вашими напрямками натисніть на кнопку 'Оплатити'",
                        'Оплачена відповідь',
                        PAY_TOKEN,
                        'UAH',
                        prices,
                        is_flexible=False,
                        start_parameter='',
                        photo_url="https://www.freepnglogos.com/uploads/visa-and-mastercard-logo-26.png",
                        photo_height=100,
                        photo_width=400,
			photo_size=400)
    
    
    def form_user_callback(self, action, user_id=""):
        return f"User;{action};{user_id};"
    
    def send_full_results_answear(self, user: User):
        err = False
        params = dumps(convert_request_form_into_params(user.request_form))
        resp = requests.request(method='get', 
                                url=f"{SERVER_LINK}/get_full_info/", 
                                data=params,
                                headers={'Authorization': f'Bearer {API_TOKEN}'})
        if resp.status_code == 200:
            courses = resp.json()['courses']        
            if courses:
                paid_text = InterfaceMessages.objects.filter(name="InterfaceMessages").first().paid_answear_text
                self.bot.send_message(user.chat_id, text=paid_text)
                for course in courses:
                   self.bot.send_message(chat_id=user.chat_id, text=convert_course_into_msg(course), parse_mode="HTML", disable_web_page_preview=True)
            else:
                err = True
        else:
            err = True
        if err:
            self.bot.send_message(chat_id=user.chat_id, text="Від час виконання Вашого запиту сталася помилка. Зверніться до адміністатора @OfficeMapIT")

def convert_course_into_msg(course):
    res = f"<b>Школа:</b> <u>{course[0]}</u>\n"\
            f"<b>Курс</b>: <u>{course[1]}</u>\n"\
            f"<b>Телефон:</b> {'+'+str(int(course[2]))} {',  +'+str(int(course[3])) if course[3] else ''}\n"\
            f'<a href="{course[4]}">Веб-стокінка школи</a>\n'
    if course[5]:
        res += f'<a href="{course[5]}">Facebook</a>\n'
    if course[6]:
        res += f'<a href="{course[6]}">Instagram</a>\n'
    return res
 
def get_user_topics_response(user: User):
    params = dumps(convert_request_form_into_params(user.request_form))
    resp = requests.request(method='get', 
                            url=f"{SERVER_LINK}/courses_topics/", 
                            data=params,
                            headers={'Authorization': f'Bearer {API_TOKEN}'})
    if resp.status_code == 200:
        topics = resp.json()['topics']
        free_answears = InterfaceMessages.objects.filter(name="InterfaceMessages").first().free_answear_text
        result = free_answears[0]
        if topics:
            for topic in topics:
                result+=f"📌 {topic}\n"
            result+=free_answears[1]
        else:
            result = "Нажаль за вашим запитом не знайдено жодного курсу"
    else:
        result = "Можливо сталася помилка. Зверніться до адміністатора @OfficeMapIT"
    return result, bool(topics)

def convert_request_form_into_params(form:dict) -> dict:
    params = {
        'age_group': AGE_GROUPS.index(form['child_age'])+1,
        # TODO: shouldn't get anything if both selected
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
