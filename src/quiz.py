import re
from time import sleep
from typing import Iterator, Callable
from telebot import TeleBot
from telebot.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from src.utils import reply_keyboard_columns_generator
from src.schemas import User, Quiz, Question

CANCEL_BUTTON_TEXT = "Скасувати"

class InputException(Exception):
    pass

def send_welcome_message_and_start_quiz(user: User, bot, user_section ):
    bot.send_message(user.chat_id, text="Привіт, тут ти зможеш знайти курси шоб твої нащадки стали розумнішими)")
    final_func = user_section.send_start_menu
    start_registration_quiz(user, bot, final_func)

def start_registration_quiz(user: User, bot: TeleBot, final_func: Callable):
    reg_quiz = Quiz.objects.filter(name="RegistrationQuiz").first()
    reg_quiz_questions = reg_quiz.questions

    quiz_iterator = iter(reg_quiz_questions)
    question = next(quiz_iterator)

    sleep(2)

    send_question(
        user,
        bot,
        question,
        quiz_iterator,
        save_func=save_registration_answers,
        final_func=final_func,
        answears={},
        is_required=reg_quiz.is_required,
    )

def start_testing_quiz(user: User, bot: TeleBot, final_func: Callable):
    testing_quiz = Quiz.objects.filter(name="TestingQuiz").first()
    questions = testing_quiz.questions

    quiz_iterator = iter(questions)
    question = next(quiz_iterator)

    sleep(2)

    send_question(
        user,
        bot,
        question,
        quiz_iterator,
        save_func=save_testing_answears,
        final_func=final_func,
        answears={},
        is_required=testing_quiz.is_required,
    )

def send_question(user: User, 
                  bot: TeleBot, 
                  question: Question, 
                  quiz_iterator: Iterator,
                  final_func: Callable = None,
                  answears=None,
                  save_func=None,
                  is_first_try=True,
                  is_required=True):
    """
    :param user: user from DB
    :param bot: telebot instance
    :param question: question to send and process
    :param quiz_iterator: iterator on questions
    :param save_func: function that will save all data from quiz
        It must receive 2 params user: User and answears: dict
    :param final_func: function that will be called after the quiz
        It must receive 1 param user: User
    :param answears: temp dictionary where all the data will be stored
    :param is_first_try: show if it is first time to answer a question.
        After wrong answer we do not need to repeat a question
    :param is_required: is quiz can be canceled
    """
    chat_id = user.chat_id
    text = question.message
    answer_markup = create_answer_markup(question, is_required=is_required)
    if is_first_try:
        bot.send_message(chat_id, text, reply_markup=answer_markup)

    bot.register_next_step_handler_by_chat_id(chat_id, process_message,
                                              user=user, bot=bot, question=question,
                                              quiz_iterator=quiz_iterator, final_func=final_func,
                                              save_func=save_func, answears=answears, 
                                              is_first_try=is_first_try, is_required=is_required)

def process_message(message: Message, **kwargs):
    """
    :param user: user from DB
    :param bot: telebot instance
    :param question: question to send and process
    :param quiz_iterator: iterator on questions
    :param save_func: function that will save all data from quiz
    :param final_func: function that will be called after the quiz
    :param answears: temp dictionary where all the data will be stored
    :param is_first_try: show if it is first time to answer a question.
        After wrong answer we do not need to repeat a question
    """
    user = kwargs["user"]
    bot = kwargs["bot"]
    question = kwargs["question"]
    quiz_iterator = kwargs["quiz_iterator"]
    save_func = kwargs["save_func"]
    final_func = kwargs["final_func"]
    answears = kwargs["answears"]
    is_first_try = kwargs["is_first_try"]
    is_required = kwargs["is_required"]

    content_type = message.content_type

    try:
        if content_type == question.input_type:
            if content_type == "text":
                valid_msg = process_text_messages( message, question, bot, user, is_required_quiz=is_required)
                if not valid_msg:
                    return
                else:
                    answears[question.name] = message.text

            elif content_type == "contact":
                contact = message.contact
                phone = contact.phone_number
                user_id = contact.user_id
                answears["phone"] = phone
                answears["user_id"] = user_id
            else:
                raise InputException

            if question.correct_answer_message:
                bot.send_message(user.chat_id,text=question.correct_answer_message,reply_markup=ReplyKeyboardRemove())
                sleep(0.5)
                
            question = next(quiz_iterator, None)
            is_first_try = True
        else:
            raise InputException

    except InputException:
        is_first_try = False
        bot.send_message(user.chat_id, text=question.wrong_answer_message)
        sleep(0.5)

    # do the next step
    if question:
        # add validation of previous answears
        send_question(
            user=user,
            bot=bot,
            question=question,
            quiz_iterator=quiz_iterator,
            save_func=save_func,
            final_func=final_func,
            answears=answears,
            is_first_try=is_first_try,
            is_required=is_required,
        )
    # if questions ended
    else:
        # save data if needed
        if save_func:
            save_func(user, answears)

        # send step after finish
        if final_func:
            final_func(user)

def process_text_messages(message: Message,
                          question: Question,
                          bot: TeleBot,
                          user: User,
                          is_required_quiz: bool):
    input_text = message.text
    if is_required_quiz is False and input_text == CANCEL_BUTTON_TEXT:
        bot.send_message(
            user.chat_id,
            text="Форма скасована \n Тисни /start щоб продовжити",
            reply_markup=ReplyKeyboardRemove(),
        )
        return False

    if question.allow_user_input:
        if question.regex:
            pattern = re.compile(question.regex)
            if not pattern.search(input_text):
                raise InputException
    else:
        if input_text not in question.buttons:
            raise InputException
    if question.max_text_size is not None:
        if len(input_text) > question.max_text_size:
            raise InputException
    return True

def create_answer_markup(question: Question, is_required: bool) -> ReplyKeyboardMarkup:
    answer_markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

    if question.input_type == "text":
        columns = 2 if len(question.buttons) < 8 else 3
        for row in reply_keyboard_columns_generator(list(question.buttons), col=columns):
            answer_markup.add(*row)

    elif question.input_type == "contact":
        answer_btn = KeyboardButton(text=question.buttons[0], request_contact=True)
        answer_markup.add(answer_btn)

    # cancel button
    if is_required is False:
        cancel_btn = KeyboardButton(text=CANCEL_BUTTON_TEXT)
        answer_markup.add(cancel_btn)

    return answer_markup

def save_registration_answers(user: User, answears):
    answears['registered'] = True
    for field in ["name", "phone", "email", "registered"]:
        setattr(user, field, answears[field])
    user.save()

def save_testing_answears(user: User, answears):
    user.request_form = answears
    user.save()