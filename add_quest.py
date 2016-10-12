# -*- coding: utf-8 -*-
'''Добавление квестов

Ввести название квеста, описание, фото,
Добавить вопрос.
Описание, фото, тип ответа, верный ответ (координаты можно координатами или локацией + точность + подсказка по метрам.)

PaVel 10.2016
'''
import db_connector, utils, standard
import json
from telebot import types

bot = None
message = None
opAddQest = 'add_quest' #Операция для таблицы операций.
operation, status, additional_info = ('', '', dict()) #операция, статус - текст, доп.инфа - словарь

question_types = {'GPS координаты': 'geo',
                  'Текст': 'text',
                  'Число': 'dig',
                  }

def put_operations():
    db_connector.put_user_operation(message.from_user.id, operation=opAddQest, status=status,
                                    additional_info=json.dumps(additional_info))

def ask_quest_name():
    global status, additional_info
    bot.send_message(message.chat.id, 'Вы собираетесь добавить новый квест. Введите его название.', reply_markup=types.ReplyKeyboardHide())
    status = 'need_quest_name'
    put_operations()

def take_quest_name():
    global status, additional_info
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Введите название квсета или нажмите /cancel',
                         reply_markup=types.ReplyKeyboardHide())
        return

    additional_info['quest_name']=message.text
    bot.send_message(message.chat.id, 'Введите описание квеста.',
                     reply_markup=types.ReplyKeyboardHide())
    status = 'need_quest_desc'
    put_operations()

def take_quest_desc():
    global status, additional_info
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Введите описание квеста или нажмите /cancel',
                         reply_markup=types.ReplyKeyboardHide())
        return

    additional_info['quest_desc'] = message.text
    bot.send_message(message.chat.id, 'Приложите фото квеста или нажмите /skip - квест без фото.',
                     reply_markup=types.ReplyKeyboardHide())
    status = 'need_quest_photo'
    put_operations()

def take_quest_photo():
    global status, additional_info
    if not (message.content_type in ['photo', ] \
            or (message.content_type == 'text' and utils.text_lower_wo_command(message) in ('skip', 'пропустить'))):
        bot.send_message(message.chat.id, 'Приложите фото квеста или нажмите /skip - квест без фото.',
                         reply_markup=types.ReplyKeyboardHide())
        return

    file_id = None
    if message.content_type == 'photo':  file_id = message.photo[-1].file_id

    #additional_info['photo_id'] = file_id

    name = additional_info.pop('quest_name', None)
    desc = additional_info.pop('quest_desc', None)
    quest_id = db_connector.add_new_quest(name=name, user_id=message.from_user.id, description=desc, photo_id=file_id)
    additional_info['quest_id'] = quest_id
    put_operations()
    ask_question_desk()

def ask_question_desk():
    global status, additional_info
    bot.send_message(message.chat.id, 'Введите название вопроса',
                     reply_markup=types.ReplyKeyboardHide())
    status = 'need_question_desc'
    put_operations()

def take_question_desc():
    global status, additional_info
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Введите описание квеста или нажмите /cancel',
                         reply_markup=types.ReplyKeyboardHide())
        return

    additional_info['question_desc'] = message.text
    bot.send_message(message.chat.id, 'Приложите фото к вопросу или нажмите /skip - вопрос без фото.',
                     reply_markup=types.ReplyKeyboardHide())
    status = 'need_question_photo'
    put_operations()

def take_question_photo():
    global status, additional_info
    if not (message.content_type in ['photo', ] \
                    or (
                message.content_type == 'text' and utils.text_lower_wo_command(message) in ('skip', 'пропустить'))):
        bot.send_message(message.chat.id, 'Приложите фото к вопросу или нажмите /skip - вопрос без фото.',
                         reply_markup=types.ReplyKeyboardHide())
        return

    file_id = None
    if message.content_type == 'photo':  file_id = message.photo[-1].file_id
    additional_info['question_photo_id'] = file_id
    put_operations()
    ask_question_type()

def ask_question_type():
    global status, additional_info

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for k in question_types.keys():
        markup.row(k)

    status = 'need_question_type'
    put_operations()
    bot.send_message(message.chat.id, 'Выберите тип вопроса кнопкой ниже',
                     reply_markup=markup)

def take_question_type():
    global status, additional_info
    if message.content_type != 'text' or message.text not in question_types.keys():
        bot.send_message(message.chat.id, 'Введите описание квеста или нажмите /cancel',
                         reply_markup=types.ReplyKeyboardHide())
        return

    additional_info['quest_type'] = question_types.get(message.text)
    status = 'need_question_answer'
    put_operations()
    additional_info['answer_step'] = 'start'
    ask_take_question_answer()


def ask_take_question_answer():
    global status, additional_info
    quest_type = additional_info.get('quest_type')
    step = additional_info.get('answer_step')

    def ask_text():
        additional_info['answer_step'] = 'take_text'
        put_operations()
        bot.send_message(message.chat.id, 'Введите текст правильного ответа',
                         reply_markup=types.ReplyKeyboardHide())

    def ask_digit():
        additional_info['answer_step'] = 'take_dig'
        put_operations()
        bot.send_message(message.chat.id, 'Введите правльный ответ (число)',
                         reply_markup=types.ReplyKeyboardHide())

    def ask_coords():
        additional_info['answer_step'] = 'take_gps'
        put_operations()
        bot.send_message(message.chat.id, 'Пришлите геолокацию правильного ответа. Либо точкой на карте, либо 2 числа через проел координаты широта, долгота в формате как в примере 55.809913 37.462587',
                         reply_markup=types.ReplyKeyboardHide())

    def ask_geo_help():
        additional_info['answer_step'] = 'take_geo_help'
        put_operations()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row('Да')
        markup.row('Нет')
        bot.send_message(message.chat.id, 'При неверном ответе показывать расстояние до цели? Выберите ответ кнопкой.',
                         reply_markup=markup)

    def save_question():
        additional_info.pop('answer_step', None)
        quest_id = additional_info.get('quest_id')
        description = additional_info.pop('question_desc', None)
        photo = additional_info.pop('question_photo_id', None)
        answer_type = additional_info.pop('quest_type', None)
        correct_answer = additional_info.pop('answer', None)
        db_connector.add_new_question(quest_id, description, photo, answer_type, correct_answer)
        ask_more_questions()

    error_flag = False
    if step == 'start':
        if quest_type == 'text': ask_text()
        elif quest_type == 'dig': ask_digit()
        elif quest_type == 'geo': ask_coords()
    elif step in('take_text', 'take_dig'):
        if message.content_type != 'text':
            error_flag = True
        else:
            additional_info['answer'] = message.text.lower()
            save_question()
    elif step == 'take_gps':
        if message.content_type == 'location':
            additional_info['lat'] = message.location.latitude
            additional_info['long'] = message.location.longitude
            ask_geo_help()
        elif message.content_type == 'text':
            coords=message.text.split()
            if len(coords) == 2 and coords[0].replace('.','',1).isdigit() and coords[1].replace('.','',1).isdigit():
                additional_info['lat'] = float(coords[0])
                additional_info['long'] = float(coords[1])
                ask_geo_help()
            else:
                error_flag = True
        else:
            error_flag = True
    elif step == 'take_geo_help':
        if message.content_type == 'text' and utils.text_lower_wo_command(message) in ('да', 'нет'):
            answer={}
            answer['lat'] = additional_info.pop('lat',0)
            answer['long'] = additional_info.pop('long',0)
            answer['accur'] = 50
            answer['hint_meters'] = utils.text_lower_wo_command(message)=='да'
            additional_info['answer'] = json.dumps(answer)
            save_question()
        else:
            ask_geo_help()

    if error_flag:
        additional_info['answer_step'] = 'start'
        put_operations()
        bot.send_message(message.chat.id, 'Неверный формат.', reply_markup=types.ReplyKeyboardHide())
        ask_take_question_answer()


def ask_more_questions():
    global status, additional_info
    status  = 'need_more_questions'
    put_operations()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row('Да')
    markup.row('Нет')
    bot.send_message(message.chat.id, 'Добавить ещё вопрос?',
                     reply_markup=markup)

def answer_more_questions():
    global status, additional_info
    if message.content_type == 'text' and utils.text_lower_wo_command(message) in ('да', 'нет'):
        if utils.text_lower_wo_command(message) == 'да':
            ask_question_desk()
        elif utils.text_lower_wo_command(message) == 'нет':
            finish()
    else:
        ask_more_questions()

def finish():
    quest_id = additional_info.get('quest_id')
    db_connector.activate_quest(quest_id)
    db_connector.put_user_operation(message.from_user.id)
    bot.send_message(message.chat.id, "Квест добавлен. Спасибо.",
                     reply_markup=standard.standard_keyboard(message.from_user.id))

def cancel_adding():
    db_connector.put_user_operation(message.from_user.id)
    bot.send_message(message.chat.id, "Ввод квеста отменён",
                     reply_markup=standard.standard_keyboard(message.from_user.id))

def add_quest_flow(bot_in, message_in):
    """Основной поток маршрутизации для квестовой части бота.

    @Можно добавить в словарь проверку на типы ответа. Или вынести в функции
    Принимает объекты bot, message
    Если это первый вызов, то выдаст список квестов, """
    status_dic = {
        'need_quest_name': take_quest_name,
        'need_quest_desc': take_quest_desc,
        'need_quest_photo': take_quest_photo,
        'need_question_desc': take_question_desc,
        'need_question_photo': take_question_photo,
        'need_question_type': take_question_type,
        'need_question_answer': ask_take_question_answer,
        'need_more_questions': answer_more_questions,
    }
    global operation, status, additional_info, bot, message
    bot = bot_in
    message = message_in
    (operation, status, additional_info) = db_connector.get_user_operation(message.from_user.id)
    if additional_info:
        additional_info = json.loads(additional_info)
    else:
        additional_info = dict()
    if not operation or operation != opAddQest:
        ask_quest_name()
    elif utils.text_lower_wo_command(message) in ('cancel', 'отмена'):
        cancel_adding()
    else:
        status_dic[status]()