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


def put_user_operation(tid, operation=None, status=None, additional_info=None):
    """Сохранить в БД инфу об операции пользователя.

    id - TelegramID пользователя. message.from_user.id
    Вариант put_user_operation(id) - очищает записи об операциях пользователя.
    """
    session = DBSession()
    operation = Operation(telegramid=tid, current_operation=operation, operation_status=status,
                          additional_info=additional_info)
    session.merge(operation)
    session.commit()
    session.close()
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


def last_users():
    session = DBSession()
    count = session.query(User).count()
    last_users_list = session.query(User).order_by(desc(User.registrationDate)).limit(10)
    session.close()
    last = []
    for u in last_users_list:
        last.append('{}. {}'.format(u.name, u.registrationDate))
    return [count, last]


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
    operation = Operation()
    tid = None
    if message:
        tid = message.from_user.id
        if from_who == 'user':
            if message.content_type == 'text':
                msg_text = message.text
            if message.content_type == 'contact':
                msg_text = str(message.contact)

        operation = get_user_operation(message.from_user.id)

    session = DBSession()
    log = Log(datetime=datetime.datetime.now(), from_who=from_who, user_id=tid, msg_text=msg_text,
              msg_type=message_type, operation=operation.current_operation, status=operation.operation_status,
              additional_info=operation.additional_info, function=inspect.stack()[1][3], comment=comment_text)
    session.add(log)
    session.commit()
    session.close()


def last_log_rec(last=10):
    session = DBSession()
    last_recs = session.query(Log).order_by(Log.datetime).limit(last)
    session.close()
    return 'Последние записи из лога. Количество {}:\n'.format(last) + '\n'.join(last_recs)


# Операции работы с таблицами квестов
def get_quest_list():
    """Получить список квестов
    """
    sql = '''select ID, Name, Description from quest_quest where Active=1'''
    (db, cursor) = sql_lite_connect()
    cursor.execute(sql, )
    result = cursor.fetchall()
    sql_lite_close(db)
    return result


def get_quest(id):
    """Получить список квестов
    """
    sql = '''select Name, Description, Photo from quest_quest where ID=?'''
    (db, cursor) = sql_lite_connect()
    cursor.execute(sql, (id,))
    result = cursor.fetchone()
    sql_lite_close(db)
    return result


def get_next_question(quest_id, question_id=None):
    """Получить следующий вопрос (или первый)
    """
    sql_t = '''select ID, description, photo, answer_type, correct_answer from quest_task
        where Active=1 {}
        and quest_id=?
        order by sequence
        limit 1'''
    sql_next = 'and sequence>(select sequence from quest_task where id={})'
    sql_first = ''
    if question_id:
        sql = sql_t.format(sql_next.format(question_id))
    else:
        sql = sql_t.format(sql_first)
    (db, cursor) = sql_lite_connect()
    cursor.execute(sql, (quest_id,))
    result = cursor.fetchone()
    sql_lite_close(db)
    return result


def get_question(question_id):
    """Получить вопрос по id
    """
    sql = '''select ID, description, photo, answer_type, correct_answer from quest_task
        where Active=1 and ID=?'''
    (db, cursor) = sql_lite_connect()
    cursor.execute(sql, (question_id,))
    result = cursor.fetchone()
    sql_lite_close(db)
    return result


def add_new_quest(user_id, name, description, photo_id):
    sql = 'insert into quest_quest (Name, Author, Description, Photo, Active) select ?, Name, ?, ?, 0 from Users where Telegramid= ?'
    (db, cursor) = sql_lite_connect()
    cursor.execute(sql, (name, description, photo_id, user_id))
    id = cursor.lastrowid
    sql_lite_close(db)
    return id


def add_new_question(quest_id, description, photo, answer_type, correct_answer):
    sql = '''insert into quest_task (quest_id, sequence, Description, Photo, answer_type, correct_answer)
            values (?, ?, ?, ?, ? ,?)'''
    sql_get_max = 'select max(sequence) from quest_task where quest_id = ?'
    (db, cursor) = sql_lite_connect()
    cursor.execute(sql_get_max, (quest_id,))
    seq = cursor.fetchone()
    if seq[0]:
        seq = seq[0] + 1
    else:
        seq = 1
    cursor.execute(sql, (quest_id, seq, description, photo, answer_type, correct_answer))
    sql_lite_close(db)


def activate_quest(quest_id, activate=True):
    sql = 'update quest_quest set active=? where ID=?'
    (db, cursor) = sql_lite_connect()
    cursor.execute(sql, (1 if activate else 0, quest_id,))
    sql_lite_close(db)
# /Операции работы с таблицами квестов