from email.policy import default
from urllib import request
import mongoengine as me

class SimpleButton(me.EmbeddedDocument):
    name = me.StringField()
    text = me.StringField()
    photo = me.StringField()
    url_link = me.StringField()
    url_text = me.StringField()

class User(me.Document):
    chat_id = me.IntField(required=True, unique=True)
    name = me.StringField(required=True)
    surname = me.StringField(required=True)
    username = me.StringField(required=True)
    phone = me.StringField(reqired=True)
    email = me.StringField(required=True)
    registered = me.BooleanField(required=True)
    request_form = me.DictField(default=None)
    is_blocked = me.BooleanField(default=False)

class Question(me.EmbeddedDocument):
    name = me.StringField(required=True)
    message = me.StringField(required=True)
    buttons = me.ListField(default=list())
    input_type = me.StringField(choices=["text", "contact"], default="text")
    max_text_size = me.IntField(max_value=4000)
    allow_user_input = me.BooleanField(default=True)
    regex = me.StringField(default=None)
    correct_answer_message = me.StringField(defaul=None)
    wrong_answer_message = me.StringField(default="Неправильний формат!")

class Quiz(me.Document):
    name = me.StringField(required=True)
    questions = me.ListField(me.EmbeddedDocumentField(Question), default=list())
    is_required = me.BooleanField(default=False)

class InterfaceMessages(me.Document):
    name = me.StringField(required=True)
    welcome_text = me.StringField(required=True)
    city_wrong_input_answear = me.StringField(required=True)
    start_menu_text = me.StringField(required=True)
    free_answear_text = me.ListField(default=list())
    paid_answear_text = me.StringField(reqired=True)
    info_text = me.StringField(required=True)