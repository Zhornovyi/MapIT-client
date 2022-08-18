import mongoengine as me
from logging import getLogger, INFO
from telebot import TeleBot
from src.schemas import Quiz, Question

logger = getLogger("course_bot")
logger.setLevel(INFO)

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
        
    def commit_registration_quiz(self):

        quiz = Quiz(name="RegistrationQuiz", is_required=True)

        q_name = Question(name="name",
                                  message="Введіть своє імʼя:",
                                  correct_answer_message="Приємно познайомитись 🥰",
                                  wrong_answer_message="Введи ім’я текстом 🤡",
        )
        q_contact = Question(name="contact",
                             message="Обміняємося контактами?",
                             buttons=["Тримай!"],
                             input_type="contact",
                             correct_answer_message="Дякую. А я залишаю тобі контакт головного організатора: @Slavkoooo 🥰",
                             wrong_answer_message="Надішли, будь ласка, свій контакт 🤡",
        )
        q_email = Question(name="email",
                           message="Наостанок, вкажи адресу своєї поштової скриньки.",
                           regex="^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$",
                           correct_answer_message="Дякую 🥰",
                           wrong_answer_message="Введи, будь ласка, електронну адресу 🤡")

        quiz.questions = [q_name, q_contact, q_email]
        quiz.save()

    def commit_testing_quiz(self):
        quiz = Quiz(name="TestingQuiz", is_required=False)
        q_age = Question(
            name="child_age",
            message="Введіть вік дитини",
            buttons=[
                "6-8 років",
                "9-11 років",
                "12-14 років",
                "15+ років",
            ],
            allow_user_input=False,
            correct_answer_message="Супер",
            wrong_answer_message="Обери відповідь у меню",
        )

        q_sex = Question(
            name="sex",
            message="Введіть стать дитини?",
            buttons=["Хлопчик", "Дівчинка"],
            correct_answer_message="Записав",
            allow_user_input=False,
            wrong_answer_message="Обери відповідь у меню",
        )

        q_format = Question(
            name="format",
            message="Введіть бажаний формат проведення занять.",
            buttons=["Online", "Offline", "Розгляну обидва варіанти"],
            correct_answer_message="Дякую 🥰",
            wrong_answer_message="Обери відповідь у меню",
            allow_user_input=False,
        )
        # must be added only if q_format
        q_city = Question(
            name="city",
            message="Введіть місто відвідування занять.",
            correct_answer_message="Дякую 🥰",
            max_text_size=30,
            wrong_answer_message="Ми не можемо нічого запропонувати у даному місті, можливо хочете обрати інше?",
        )
        q_type = Question(
            name="type",
            message="Який тип занять оберете?",
            buttons=["Групові", "Індивідуальні"],
            correct_answer_message="Записав",
            wrong_answer_message="Обери відповідь у меню",
            allow_user_input=False,
        )
        q_thinking = Question(
            name="thinking",
            message="Оберіть тип мислення дитини?",
            buttons=["Творчий", "Логічний"],
            correct_answer_message="Записав",
            wrong_answer_message="Обери відповідь у меню",
            allow_user_input=False,
        )
        # must be added only if q_thinking 
        q_exp_it = Question(
            name="experience_it",
            message="Чи має дитина досвід програмування?",
            buttons=["Має", "Немає"],
            correct_answer_message="Записав",
            wrong_answer_message="Обери відповідь у меню",
            allow_user_input=False,
        )
        # must be added only if q_format 
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



