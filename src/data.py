import mongoengine as me
from os import environ
from logging import getLogger, INFO
from telebot import TeleBot
from src.schemas import Quiz, Question, InterfaceMessages

logger = getLogger("course_bot")
logger.setLevel(INFO)

AGE_GROUPS = ["6-8 років", "9-11 років", "12-14 років", "15+ років",]
CLASS_FORMATS = ["Online", "Offline", "Розгляну обидва варіанти"]
SERVER_LINK = environ.get("API_LINK", "http://127.0.0.1:8000")
API_TOKEN = environ.get("API_TOKEN", None)


class Data:
    def __init__(self, conn_string: str, bot: TeleBot):
        self.bot = bot
        me.connect(host=conn_string)
        logger.info("Mongo db connected successfully")
        self.add_quizes()

    def add_quizes(self):
        if len(Quiz.objects) == 0:
            self.commit_registration_quiz()
            logger.info("Registration quiz has been added")
        else:
            self.update_quiz_table()
            logger.info("Quizes have been updated")
        if Quiz.objects.filter(name="TestingQuiz").count() == 0:
            self.commit_testing_quiz()
            logger.info("Testing quiz has been added")
        
        if InterfaceMessages.objects.filter(name="InterfaceMessages").count() == 0:
            self.commit_interface_massages()
            logger.info("Interface masseges has been added.")

    def commit_registration_quiz(self):

        quiz = Quiz(name="RegistrationQuiz", is_required=True)

        q_name = Question(name="name",
                                  message="Я - бот MapIT. А тебе як звати?",
                                  correct_answer_message="Радий познайомитись!🤝",
                                  wrong_answer_message="Введи ім’я текстом",
        )
        q_contact = Question(name="contact",
                             message='Давай обміняємось контактами. Натисни кнопку "Мій номер".',
                             buttons=["Mій номер"],
                             input_type="contact",
                             correct_answer_message="Дякую! 🥰 @OfficeMapIT - люди, які знають про ІТ освіту ще більше ніж я.",
                             wrong_answer_message="Надішли, будь ласка, свій контакт",
        )
        quiz.questions = [q_name, q_contact]
        quiz.save()

    def commit_testing_quiz(self):
        quiz = Quiz(name="TestingQuiz", is_required=False)
        q_age = Question(
            name="child_age",
            message="Оберіть вік дитини:",
            buttons= AGE_GROUPS,
            allow_user_input=False,
            correct_answer_message="Супер",
            wrong_answer_message="Обери відповідь у меню",
        )

        q_sex = Question(
            name="sex",
            message="Оберіть стать дитини:",
            buttons=["Хлопчик", "Дівчинка"],
            correct_answer_message="Записав",
            allow_user_input=False,
            wrong_answer_message="Обери відповідь у меню",
        )

        q_format = Question(
            name="format",
            message="Оберіть бажаний формат навчання:",
            buttons=CLASS_FORMATS,
            correct_answer_message="Дякую 🥰",
            wrong_answer_message="Обери відповідь у меню",
            allow_user_input=False,
        )
        q_city = Question(
            name="city",
            message="Введіть місто відвідування занять:",
            correct_answer_message="Дякую 🥰",
            max_text_size=30,
            wrong_answer_message="Покощо не маю що запропонувати у цьому місті",
        )
        q_type = Question(
            name="type",
            message="Оберіть тип занять:",
            buttons=["Групові", "Індивідуальні"],
            correct_answer_message="Записав",
            wrong_answer_message="Обери відповідь у меню",
            allow_user_input=False,
        )
        q_thinking = Question(
            name="thinking",
            message="Оберіть тип мислення дитини:",
            buttons=["Творчий", "Логічний"],
            correct_answer_message="Записав",
            wrong_answer_message="Обери відповідь у меню",
            allow_user_input=False,
        )
        q_exp_it = Question(
            name="experience_it",
            message="Чи має дитина досвід програмування?",
            buttons=["Має", "Немає"],
            correct_answer_message="Записав",
            wrong_answer_message="Обери відповідь у меню",
            allow_user_input=False,
        )
        q_exp_online = Question(
            name="experence_online",
            message="Чи має дитина досвід онлайн навчання?",
            buttons=["Має", "Немає"],
            correct_answer_message="Записав",
            wrong_answer_message="Обери відповідь у меню",
            allow_user_input=False,
        )

        quiz.questions = [
            q_age,
            q_sex,
            q_format,
            q_city,
            q_type,
            q_thinking,
            q_exp_it,
            q_exp_online
        ]
        quiz.save()
    
    def update_quiz_table(self):
        quizes = Quiz.objects

        # form paragraphs in questions
        for quiz in quizes:
            for question in quiz.questions:
                question.message = question.message.replace("\\n", "\n")

            quiz.save()

    def commit_interface_massages(self):
        table = InterfaceMessages(name="InterfaceMessages")
        table.welcome_text = "Привіт! Я - бот, що знає все про ІТ освіту дітей та підлітків в Україні. 🇺🇦 " \
                             "Розкажи мені про майбутнього айтішника, а я допоможу обрати напрям навчання, " \
                             "а потім розкажу де можна цьому навчитись (курс та школа). 💻"
        table.city_wrong_input_answear = "Не можу знайти заняття у твоєму місті. "\
                                         "Ось перілік доступних міст. Якщо не знайшов "\
                                         "свого міста продовжуй пошук курсів онлайн формату\n"
        table.start_menu_text = "Супер! Попереду міні-тест з 8 простих питань, які допоможуть обрати напрям навчання"
        table.free_answear_text = ["Дякуємо за вашу довіру! Ми проаналізували відповіді та рекомендуємо такі напрямки навчання \xF0\x9F\x91\x87\n", 
                                   "\nВ країні багато навчальних закладів, де навчають юних айтішників, і ми обрали найкращі саме для вашої дитини.\n\n"
                                   "Щоб отримати список шкіл за вашими напрямками натисніть на кнопку 'Отримати'\n\n"
                                   "`[Договір публічної оферти] (https://drive.google.com/file/d/14c0K6gxz0CEGA-WFkwelc62Ct_bwNpY9/view?usp=sharing)`\n"
                                   "`[Політика конфіденційності] (https://drive.google.com/file/d/1UaYczwfsdliKAbxrwFHBIePdNaBAQNOd/view?usp=sharing`)`"]
        table.paid_answear_text =  ""
        
        table.save()
        


