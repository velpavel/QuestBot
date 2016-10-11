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
operation, status, additional_info = ('', '', dict()) #операция, статус - текст, доп.инфа - словарь

def put_operations():
    db_connector.put_user_operation(message.from_user.id, operation=opDoQest, status=status,
                                    additional_info=json.dumps(additional_info))

def show_quest_list():
    """Отображение списка квестов.

    @Написано, не тестировано
    В   additional_info['buttons-quest_id'] пишет текст кнопки - id квеста"""
    quest_list = db_connector.get_quest_list()
    if not quest_list:
        bot.send_message(message.chat.id,'Нет квесвтов', reply_markup=standard.standard_keyboard(message.from_user.id))
        return
    text='Список доступных квестов:\n'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    additional_info['buttons-quest_id']={}
    for i in range(len(quest_list)):
        #структура id, Name, description
        text+='{}) {}: {}'.format(i+1, quest_list[i][1], quest_list[i][2])
        markup.row('{}) {}\n'.format(i+1, quest_list[i][1]))
        additional_info['buttons-quest_id']['{}) {}'.format(i+1, quest_list[i][1])]= quest_list[i][0]
    text+='\nВыбери свой квсет кнопкой ниже.'
    bot.send_message(message.chat.id, text, reply_markup=markup)
    status = 'neead_quest_choice'
    put_operations()

def give_quest():
    """Отправка квеста.

    @Не написано
    Предполагается с кнопкой "начать" - нуно чтобы дать пользователь возможность выйти на исходную позицию, если надо.
    Можно заменить  пока на выдачу первого вопроса сразу.
    """
    quest_id = additional_info.get('buttons-quest_id',[]).get(message.text, None)
    additional_info.pop('buttons-quest_id', None)
    if not quest_id:
        #@обработка ошибки. Сообщение об ошибке и редирект на show_quest_list
        pass
    else:
        additional_info['quest_id']=quest_id
        give_question()
    #или сразу редиректить на give_question
    #status = 'need_question'
    #put_operations()

def give_question():
    """Выслать вопрос TSS

    @Не написано
    Типы вопросов
    text
    dig
    geo - выслать кнопку запроса координат.
    """
    quest_id = additional_info.get('quest_id')
    last_question_id = additional_info.get('question_id')
    if not quest_id:
        #Обработка ошибки
        pass
    else:
        next_quest=db_connector.get_next_question(quest_id=quest_id, question_id=last_question_id)
        if next_quest:
            #Структура ID, description, answer_type, correct_answer
            (question_id, description, answer_type, correct_answer) = next_quest
            if answer_type=='geo':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                markup.add(types.KeyboardButton(text=r'Вышел на точку!', request_location=True))
            else:
                markup = types.ReplyKeyboardHide()

            #Тут отправка текста вопроса с клавиатурой.
            additional_info['question_id']=question_id
            status = 'need_answer'
            put_operations()
        else:
            finish_quest()

def check_answer():
    """Проверка правильности ответа на вопрос.

    Типы вопросов и как хранятся в БД
    text   'да'
    dig    '4'
    geo    {'lat': 55.809913, 'long': 37.462587, 'accur': 50, 'hint_meters': True}
    """
    pass

def cancel_quest():
    pass

def finish_quest():
    pass

def quest_flow(bot_in, message_in):
    """Основной поток маршрутизации для квестовой части бота.

    Принимает объекты bot, message
    Если это первый вызов, то выдаст список квестов, """
    status_dic = {
        'neead_quest_choice': give_quest(),
        'need_question': give_question(),
        'need_answer': check_answer(),
    }
    global operation, status, additional_info, bot, message
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
        status_dic[status]