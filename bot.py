# -*- coding: utf-8 -*-
'''Файл для запуска бота.
Здесь же маршрутизация сообщения.

PaVel 09.2016
'''
import telebot
import configparser
import datetime, time
from telebot import types

import db_connector
from registration import register_flow
import admin_functions


#import logging
#logger = telebot.logger
#telebot.logger.setLevel(logging.DEBUG)

config_file = r'config.ini'

config = configparser.ConfigParser()
config.read(config_file)

bot = telebot.TeleBot(config['BASE']['Token'])
admin_id = config['BASE'].get('Admin_id')
admin_id = int(admin_id) if admin_id.isdigit() else 0

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    """Обработка /start /help команд

    Необходимо менять help_str - приветсвие бота.
    При желании можно отделить help.
    Незарегистрированные пользователи перенаправлются регистрироваться.
    Текущий вариант предусматривает автоматическое заполнение admin_id.
    Логика: первый отправивший /start (/help) и становиться админом : )
    Алгоритм: если admin_id пустой, то id написавшего пользователя и становиться admin_id
    ВНИМАНИЕ! После автозаполнения admin_id требуется перезапуск бота. Чтобы считать admin_id заново.
    @! пофиксить
    """
    global admin_id
    db_connector.save_to_log('user', message)
    help_str='''Help_str'''
    #Ниже заполнение пустого admin_id
    if not admin_id:
        admin_id = str(message.from_user.id)
        config['BASE']['Admin_id'] = admin_id
        with open(config_file, 'w') as configfile:
            config.write(configfile)

    bot.send_message(message.chat.id, help_str)
    #Редирект незарегенного пользователя на регистрацию.
    if not (db_connector.is_user_registered(message.from_user.id)):
        register_flow(bot, message)

@bot.message_handler(func=lambda message: not db_connector.is_user_registered(message.from_user.id), content_types=['text','contact'])
def handle_register(message):
    """Обработка регистарции пользователя.

    Ссылается на модуль, в котором реализована регистрация пользователя.
    Перехватывает все сообщения незарегистрированного пользователя.
    По результатам в таблице users у пользователя должна быть RegistrationDone==1
    По умолчанию менять не надо, детали смотри в registration.py
    """
    db_connector.save_to_log('user', message)
    register_flow(bot, message)

@bot.message_handler(commands=admin_functions.admin_commands)
def handle_admin_com(message):
    """Функции админской "панели управления".

    Детали смотри в admin_functions.py
    Для правильной работы необходим заполненный admin_id в config
    По умолчанию менть не надо.
    """
    db_connector.save_to_log('user', message)
    admin_functions.admin_flow(bot, message)

#Сюда добавлять функции/хендлеры обработки.

@bot.message_handler(func=lambda message: True, content_types=['text', 'contact', 'photo', 'document', 'location'])
def msg(message):
    """Обработка всего, что не попало под остальные обработчики.

    В идеале сюда ничего не должно попадать.
    Предполагается изменение.
    Можно использовать как шаблон.
    """
    db_connector.save_to_log('user', message) #Сохранение входящего сообщения в БД. Для статистики.
    bot.send_message(message.chat.id, 'Рад с тобой пообщаться.', reply_markup=types.ReplyKeyboardHide())

if __name__ == '__main__':
    """Запуск бота

    По умолчанию ничего менять не надо.
    """
    def run_bot():
        """Функция для запуска прослушки телеграм сервера"""
        if admin_id: bot.send_message(admin_id, "Started")
        print("Bot started")
        db_connector.save_to_log('system', comment_text="Bot started")
        bot.polling(none_stop=True)

    #Для продуктива удобнее когда бот автоматически рестартится.
    #Для разработки удобнее получать вылет с ошибкой.
    if config['BASE']['Debug'] == '1':
        run_bot()
    else:
        while True:
            try:
                run_bot()
                break
            except Exception as e:
                err_text = "{} Error: {} : {}".format(datetime.datetime.now().strftime('%x %X'), e.__class__, e)
                print(err_text)
                print("Restarted after 20 sec")
                db_connector.save_to_log('system', comment_text=err_text)
                time.sleep(20)
