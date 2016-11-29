# -*- coding: utf-8 -*-
'''Выполнение квестов

Немного логики.
Пока юзер занимается выполнение квсета у него стоит операция opDoQest
статус показывает чем имено он занимается (как обработать пришедший от него ответ)
вся доп инфа храниться в доп инфу в json формате.
Предлагаю там хранить как минимум код квеста, код вопроса, количество данных на этот вопрос неверных ответов

необходимые обраюотки:
-Поиск квеста (поиск по названию, по координатам)
-Подтверждение выбора квеста (детальное описание, старт координаты, если есть)
-Начало квсета (сохранение времени старта)
-Отправка вопроса.
-Получение и проверка ответа.
-Конец квеста. (поздравление, сохранение врмеени)

PaVel 10.2016
'''
import db_connector, utils, standard
import json
from telebot import types

bot = None
message = None
opDoQest = 'do_quest' #Операция для таблицы операций.
oper, status, additional_info = ('', '', dict()) #операция, статус - текст, доп.инфа - словарь

def put_operations():
    db_connector.put_user_operation(message.from_user.id, operation=opDoQest, status=status,
                                    additional_info=json.dumps(additional_info))

def show_quest_list():
    """Отображение списка квестов.

    @Написано, тестируется
    В   additional_info['buttons-quest_id'] пишет текст кнопки - id квеста"""
    global status, additional_info
    quest_list = db_connector.get_quest_list()
    if not quest_list:
        bot.send_message(message.chat.id, 'Нет квестов', reply_markup=standard.standard_keyboard(message.from_user.id))
        return
    text = 'Список доступных квестов:\n'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    additional_info['buttons-quest_id']={}
    for i in range(len(quest_list)):
        #структура id, Name, description
        text += '{}) <b>{}</b>: {}\n'.format(i+1, quest_list[i][1], quest_list[i][2])
        markup.row('{}) {}'.format(i+1, quest_list[i][1]))
        additional_info['buttons-quest_id']['{}) {}'.format(i+1, quest_list[i][1])]= quest_list[i][0]
    text += '\nВыберите свой квеcт кнопкой ниже.'
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
    status = 'neead_quest_choice'
    put_operations()

def give_quest():
    """Отправка квеста.

    @Написано, тестируется
    Предполагается с кнопкой "начать" - нуно чтобы дать пользователь возможность выйти на исходную позицию, если надо.
    Можно заменить  пока на выдачу первого вопроса сразу.
    """
    global status, additional_info
    quest_id = additional_info.get('buttons-quest_id',{}).get(message.text, None)
    additional_info.pop('buttons-quest_id', None)
    if not quest_id:
        #@обработка ошибки. Сообщение об ошибке и редирект на show_quest_list
        db_connector.save_to_log('system', message=message, comment_text='Не удалось найти код квеста по кнопке')
        bot.send_message(message.chat.id, 'Нужно выбрать квест кнопкой', reply_markup=types.ReplyKeyboardHide())
        show_quest_list()
    else:
        additional_info['quest_id']=quest_id
        (name, description, photo) = db_connector.get_quest(quest_id)
        text='<b>{}</b> \n\n{}'.format(name, description)
        bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=types.ReplyKeyboardHide())
        if photo:
            bot.send_photo(message.chat.id, photo, reply_markup=types.ReplyKeyboardHide())
        bot.send_message(message.chat.id, 'Ваш квест начинается. Удачи!', reply_markup=types.ReplyKeyboardHide())
        give_question(next_q=True)

def give_question(next_q = True):
    """Выслать вопрос

    @Написано, тестируется
    Типы вопросов
    text
    dig
    geo - выслать кнопку запроса координат.
    """
    global status, additional_info
    quest_id = additional_info.get('quest_id')
    last_question_id = additional_info.get('question_id')
    if not quest_id:
        db_connector.save_to_log('system', message=message, comment_text='Не удалось найти код квеста в additional_info')
        bot.send_message(message.chat.id, 'Что-то пошло не так...', reply_markup=types.ReplyKeyboardHide())
        show_quest_list()
    else:
        if next_q:
            next_quest=db_connector.get_next_question(quest_id=quest_id, question_id=last_question_id)
        else:
            next_quest=db_connector.get_question(question_id=last_question_id)
        if next_quest:
            #Структура ID, description, answer_type, correct_answer
            (question_id, description, photo, answer_type, correct_answer) = next_quest
            if answer_type == 'geo':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                markup.add(types.KeyboardButton(text=r'Вышел на точку!', request_location=True))
            else:
                markup = types.ReplyKeyboardHide()
            additional_info['question_id']=question_id
            status = 'need_answer'
            put_operations()
            bot.send_message(message.chat.id, description, reply_markup=markup)
            if photo:
                bot.send_photo(message.chat.id, photo, reply_markup=markup)
        elif next_q:
            finish_quest()
        else:
            db_connector.save_to_log('system', message=message,
                                     comment_text='Вопрос где-то потерялся')
            bot.send_message(message.chat.id, 'Что-то пошло не так...', reply_markup=types.ReplyKeyboardHide())
            show_quest_list()

def check_answer():
    """Проверка правильности ответа на вопрос.

    @Добавить проверку на тип ответа. Всюду.
    Типы вопросов и как хранятся в БД
    text   'да'
    dig    '4'
    geo    {'lat': 55.809913, 'long': 37.462587, 'accur': 50, 'hint_meters': True}
    """
    global status, additional_info

    question = db_connector.get_question(question_id=additional_info.get('question_id'))
    if question:
        is_answer_correct = False
        add_answer_text=''
        # Структура ID, description, answer_type, correct_answer
        (question_id, description, photo, answer_type, correct_answer) = question
        if answer_type == 'geo':
            if message.content_type == 'location':
                correct_answer = json.loads(correct_answer)
                dist = utils.Distance(correct_answer['lat'], correct_answer['long'], message.location.latitude, message.location.longitude)
                if dist > correct_answer['accur']:
                    is_answer_correct = False
                    if correct_answer.get('hint_meters', False):
                        add_answer_text = '\nРасстояние до точки '+str(dist)+' метров.'
                else:
                    is_answer_correct=True
            else:
                is_answer_correct = False
                add_answer_text = '\nОтвет нужно отправить кнопкой!.'
        else:
            if message.content_type == 'text':
                if correct_answer.lower() == message.text.lower():
                    is_answer_correct = True
                else:
                    is_answer_correct = False
            else:
                is_answer_correct = False
                add_answer_text = '\nОтвет нужно отправить текстом-сообщением.'
        if is_answer_correct:
            bot.send_message(message.chat.id, 'Верно!', reply_markup=types.ReplyKeyboardHide())
            give_question(next_q=True)
        else:
            bot.send_message(message.chat.id, 'Нет! Не верно!'+add_answer_text, reply_markup=types.ReplyKeyboardHide())
            give_question(next_q=False)

    else:
        db_connector.save_to_log('system', message=message,
                                 comment_text='Вопрос где-то потерялся')
        bot.send_message(message.chat.id, 'Что-то пошло не так...', reply_markup=types.ReplyKeyboardHide())
        show_quest_list()


def cancel_quest():
    db_connector.put_user_operation(message.from_user.id)
    bot.send_message(message.chat.id, "Квест отменён",
                     reply_markup=standard.standard_keyboard(message.from_user.id))


def finish_quest():
    global status, additional_info
    db_connector.put_user_operation(message.from_user.id)
    bot.send_message(message.chat.id, "Вы победили! Поздравляю!", reply_markup=standard.standard_keyboard(message.from_user.id))

def quest_flow(bot_in, message_in):
    """Основной поток маршрутизации для квестовой части бота.

    @Можно добавить в словарь проверку на типы ответа. Или вынести в функции
    Принимает объекты bot, message
    Если это первый вызов, то выдаст список квестов, """
    status_dic = {
        'neead_quest_choice': give_quest,
        'need_question': give_question,
        'need_answer': check_answer,
    }
    global oper, status, additional_info, bot, message
    bot = bot_in
    message = message_in
    (operation, status, additional_info) = db_connector.get_user_operation(message.from_user.id)
    if additional_info:
        additional_info = json.loads(additional_info)
    else:
        additional_info = dict()
    if not operation or operation != opDoQest:
        show_quest_list()
    elif utils.text_lower_wo_command(message) in ('cancel', 'отмена'):
        cancel_quest()
    else:
        status_dic[status]()