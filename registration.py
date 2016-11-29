# -*- coding: utf-8 -*-
"""Регистраиця пользователя
Основной поток register_flow

Настраивается через config.ini
enable = 1 - включить регистраицю.
name = 1 - требовать имя пользователя
phone = 1 - требовать телефон пользователя
email = 1 - требовать email пользователя
verification_email = 1 - email требует проверки.
Для работы посдедней функции необходимо подключить почтовый сервер.
На указанный email будет высылаться код для проверки, который надо ввести в Telegram

PaVel 09.2016
"""
import db_connector
import configparser
from telebot import types
import re, random
import standard
from models import User

opRegister = 'register'

config = configparser.ConfigParser()
config.read('config.ini')
procedure = []
operation = None
user = None
session = None


def next_step(bot, message):
    global operation
    if operation.operation_status is not None:
        operation.operation_status += 1
    else:
        operation.operation_status = 0
    if operation.operation_status >= len(procedure):
        finish_reg(bot, message)
    else:
        operation.current_operation = opRegister
        operation.additional_info_db = procedure[operation.operation_status][0]
        procedure[operation.operation_status][1](bot, message)


def finish_reg(bot, message):
    user.registrationDone = 1
    db_connector.put_user_operation(session, user)
    bot.send_message(message.chat.id, 'Регистрация завершена', reply_markup=standard.standard_keyboard(message.from_user.id))


def ask_name(bot, message):
    bot.send_message(message.chat.id, 'Представьтесь. Введите ваши Фамилию и имя\nPut your first and last names.', reply_markup=types.ReplyKeyboardHide())


def check_name(bot, message):
    if message.content_type == 'text':
        user.name = message.text
        next_step(bot, message)
    else:
        ask_name(bot, message)


def ask_phone(bot, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton(text=r"Разрешить.Press", request_contact=True))
    text = 'Необходимо разрешить доступ к номеру телефона. Нажмите кнопку "Разрешить" ниже и "Ок" в появившемя окне\n Need access to phone number. Press button at the bootom, then "ok"'
    bot.send_message(message.chat.id, text, reply_markup=markup)


def check_phone(bot, message):
    if message.content_type == 'contact':
        if message.contact.user_id == message.from_user.id:
            user.phone = message.contact.phone_number
            next_step(bot, message)
        else:
            bot.send_message(message.chat.id, "Неверный телефон", reply_markup=types.ReplyKeyboardHide())
            ask_phone(bot, message)
    else:
        bot.send_message(message.chat.id,
                         'Необходимо нажать кнопки "разрешить" и во всплывшем окне ок. \n Если вы нажали кнопку, а окно не всплыло, то, скорее всего у вас старая версия Telegram. Обновите приложение через Google Play Market или AppStore. Или же зарегистрируйтесь через барузер. Версии выпущенные до апреля 2016го года не поддерживают многие функции.',
                         reply_markup=types.ReplyKeyboardHide())
        ask_phone(bot, message)


def ask_email(bot, message):
    text = 'Укажите ваш  email.'
    if config['REGISTRATION']['Verification_email']: text += ' На него будет выслан код для активации.'
    bot.send_message(message.chat.id, text, reply_markup=types.ReplyKeyboardHide())


def check_email(bot, message):
    rule = r'''^[a-z0-9\._\-]{1,128}@[a-z0-9\._\-]{1,128}\.[a-z]{2,3}$'''
    if message.content_type == 'text':
        text = message.text.lower()
        if re.search(rule, text, re.VERBOSE):
            user.email = text
            next_step(bot, message)
        else:
            bot.send_message(message.chat.id, 'Некорректный email. Попобуйте ещё раз.', reply_markup=types.ReplyKeyboardHide())
    else:
        ask_email(bot, message)


def ask_verification_email(bot, message):
    #Нужно научить высылать email
    random.seed()
    ver_code = ''
    for x in range(6): ver_code += str(random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
    text = 'Добрый день. \n\nПользователь {} с телефоном {} указал этот адрес для регистрации в DanSFA bot. Код {}'.format(
        user.name, user.phone, ver_code)
    #send.send(toaddr=[user.email, ], tocopy=[''], subj='BOT Registration', html_format=0, msg_text=text, fromaddr='bot')
    operation.status='need_verif_code'
    operation.additional_info_db = ver_code + ':0'
    bot.send_message(message.chat.id, 'На {} выслан код. Отправьте этот код боту'.format(user.email), reply_markup=types.ReplyKeyboardHide())


def check_verification_email(bot, message):
    if message.content_type == 'text':
        (ver_code, chance) = operation.additional_info_db.split(':')
        chance = int(chance) + 1
        operation.additional_info_db = ver_code + ':' + str(chance)
        if chance <= 10:
            if message.text == ver_code:
                finish_reg(bot, message)
            else:
                bot.send_message(message.chat.id, 'Неверный код. Попробуйте ещё раз.', reply_markup=types.ReplyKeyboardHide())
        else:
            bot.send_message(message.chat.id,
                             'Многократный неверный ввод. Аккаунт заблокировн. Для разблокировки пишите на админа.', reply_markup=types.ReplyKeyboardHide())
            bot.send_message(config['BASE']['Admin_id'], 'Заблокирован пользователь {}'.format(message.from_user.id))
    else:
        bot.send_message(message.chat.id, 'Введите код', reply_markup=types.ReplyKeyboardHide())


def register_flow(bot, message, _session):
    global operation, user, session
    session = _session
    user = session.query(User).filter_by(telegramid=message.from_user.id).first()
    operation = user.operation
    if not operation.current_operation or operation.current_operation != opRegister:
        if not procedure:
            user.registrationDone = 1
            db_connector.put_user_operation(session, user)
        else:
            bot.send_message(message.chat.id, "Для начала работы необходимо зарегестрироваться", reply_markup=types.ReplyKeyboardHide())
            next_step(bot, message)
    elif operation.operation_status is not None:
        operation.operation_status = int(operation.operation_status)
        procedure[operation.operation_status][2](bot, message)


if config['REGISTRATION']['Enable'] == '1':
    if config['REGISTRATION']['Name'] == '1': procedure.append(['Name', ask_name, check_name])
    if config['REGISTRATION']['Phone'] == '1': procedure.append(['Phone', ask_phone, check_phone])
    if config['REGISTRATION']['Email'] == '1': procedure.append(['Email', ask_email, check_email])
    if config['REGISTRATION']['Verification_email'] == '1' and config['REGISTRATION']['Email'] == '1':
        procedure.append(['Verification_email', ask_verification_email, check_verification_email])