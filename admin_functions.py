# -*- coding: utf-8 -*-
'''Функции админа.

PaVel 09.2016
'''
import configparser
import db_connector
from telebot import types

config = configparser.ConfigParser()
config.read('config.ini')
admin_id = config['BASE'].get('Admin_id')
admin_id = int(admin_id) if admin_id.isdigit() else 0

admin_commands = ['admin', 'last_users', 'log']

def admin_flow(bot, message):
    if message.from_user.id == admin_id:
        comm_list = message.text.lower().split(' ')
        if comm_list[0] == '/last_users':
            (count, users) = db_connector.last_users()
            bot.send_message(message.chat.id, 'Всего {} \nПоследние\n{}'.format(count, '\n'.join(users)))
        elif comm_list[0] =='/log':
            if len(comm_list)>=2: count_str = comm_list[1]
            else: count_str = 10
            result = db_connector.last_log_rec(count_str)
            bot.send_message(message.chat.id, result)
        elif comm_list[0] == '/admin':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            for command in admin_commands:
                markup.add(types.KeyboardButton('/'+command))
            bot.send_message(message.chat.id, 'Админ команды', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Нет такой команды')
    else:
        bot.send_message(message.chat.id, "Недоступно")