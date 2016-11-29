# -*- coding: utf-8 -*-
"""Работа с БД

PaVel 09.2016
"""
import inspect, datetime
from sqlalchemy import desc
from models import DBSession, User, Operation, Log


def get_session():
    return DBSession()


# Работа с user_operation.
# Текущие состояния пользователя при необходимости сохраняются в user_operation.
# current_operation - Операция (регистраиця, работа с задачами и т.п.)
# operation_status - шаг/этап операции.
# additional_info - вся необходимая доп инфа. при необходимости сохранить группу параметров использовать json
def get_user_operation(tid):
    """Получить инфу о текущей операции пользователя

    id - TelegramID пользователя. message.from_user.id
    return Operation object
    """
    session = DBSession()
    operation = session.query(Operation).filter_by(telegramid=tid).first()
    session.close()
    return operation


def put_user_operation(session, user, operation=None, status=None, additional_info=None):
    """Сохранить в БД инфу об операции пользователя.

    id - TelegramID пользователя. message.from_user.id
    Вариант put_user_operation(id) - очищает записи об операциях пользователя.
    """
    session.add(user)
    user.operation.current_operation=operation
    user.operation.operation_status=status
    user.operation.additional_info=additional_info
    user.operation.code_additional()
    #session.commit()
# /Работа с user_operation.


# Операции работы с таблицей users
def is_user_registered(tid):
    session = DBSession()
    user = session.query(User).filter_by(telegramid=tid, registrationDone=True).first()
    session.close()
    return True if user else False


def add_new_user(tid):
    session = DBSession()
    user = User(telegramid=tid)
    session.add(user)
    session.commit()
    session.close()


def get_user(tid):
    session = DBSession()
    user = session.query(User).filter_by(telegramid=tid).first()
    session.close()
    return user


def register_user(tid, phone=None, name=None, email=None, registration_done=0):
    session = DBSession()
    user = User(telegramid=tid)
    if phone: user.phone = phone
    if name: user.name = name
    if email: user.email = email
    if registration_done:
        user.registrationDone = registration_done
        user.registrationDate = datetime.datetime.now()
    session.merge(user)
    session.commit()
    session.close()

# /Операции работы с таблицей users


def save_to_log(from_who='user', message_type=None, message=None, comment_text='', msg_text=''):
    """Сохранить в лог. Внимательно передавать from_who

    from_who - 'bot', 'user', 'system'. От кого сообщение
    message - тип message. Сообщение от пользователя.
    comment_text - дополнительный текст.
    msg_text - текст сообщения. Использовать для сохранения ответа бота на message пользователя

    Примеры.
    save_to_log('user', message) - сохранить сообщение от пользователя.
    save_to_log('system', comment_text=err_text) - сохранить сообщение от системы. Например, об ошибке.
    save_to_log('bot', message=message_from_user, msg_text=bot_msg_text) - сохранить сообщение от бота пользоателю.
    """
    if from_who not in ('bot', 'user', 'system'):
        comment_text += ' ' + from_who
        from_who = 'need_help'
    operation = None
    tid = None
    session = DBSession()
    if message:
        tid = message.from_user.id
        if from_who == 'user':
            if message.content_type == 'text':
                msg_text = message.text
            if message.content_type == 'contact':
                msg_text = str(message.contact)

        operation = session.query(Operation).filter_by(telegramid=tid).first()

    if operation is None: operation = Operation()
    log = Log(datetime=datetime.datetime.now(), from_who=from_who, user_id=tid, msg_text=msg_text,
              msg_type=message_type, operation=operation.current_operation, status=operation.operation_status,
              additional_info=operation.additional_info_db, function=inspect.stack()[1][3], comment=comment_text)
    session.add(log)
    session.commit()
    session.close()


def last_log_rec(last=10):
    session = DBSession()
    last_recs = session.query(Log).order_by(Log.datetime).limit(last)
    session.close()
    return 'Последние записи из лога. Количество {}:\n'.format(last) + '\n'.join(last_recs)