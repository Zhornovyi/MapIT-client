from atexit import register
from telebot.types import Message

from src.schemas import User


def get_user(message: Message) -> User:
    user_chat_id = message.chat.id

    user = User.objects.filter(chat_id=user_chat_id)

    # add user if it does not exist
    if len(user) == 0:

        username = (
            message.chat.username
            if message.chat.username is not None
            else "No Nickname"
        )
        name = (
            message.chat.first_name
            if message.chat.first_name is not None
            else "No Name"
        )
        surname = (
            message.chat.last_name
            if message.chat.last_name is not None
            else "No Surname"
        )
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