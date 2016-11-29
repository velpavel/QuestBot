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
from models import User, Operation
from registration import register_flow, opRegister
import admin_functions, do_quest, add_quest
import standard, utils

#import logging
#logger = telebot.logger
#telebot.logger.setLevel(logging.DEBUG)

config_file = r'config.ini'

config = configparser.ConfigParser()
config.read(config_file)

bot = telebot.TeleBot(config['BASE']['Token'])
admin_id = config['BASE'].get('Admin_id')
admin_id = int(admin_id) if admin_id.isdigit() else 0

#@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message, session, user):
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
    help_str='''Добро пожаловать.

    Здесь можно проходить квесты - приключения в реальности. Выбирите себе квест и наслаждайтесь.'''
    #Ниже заполнение пустого admin_id
    if not admin_id:
        admin_id = str(message.from_user.id)
        config['BASE']['Admin_id'] = admin_id
        with open(config_file, 'w') as configfile:
            config.write(configfile)

    bot.send_message(message.chat.id, help_str)
    #Редирект незарегенного пользователя на регистрацию.
    if not (user.registrationDone):
        register_flow(bot, message, session)


#@bot.message_handler(func=lambda message: True, content_types=['text', 'contact', 'photo', 'document', 'location'])
def not_found(message):
    """Обработка всего, что не попало под остальные обработчики.

    В идеале сюда ничего не должно попадать.
    Предполагается изменение.
    Можно использовать как шаблон.
    """
    bot.send_message(message.chat.id, 'Рад с тобой пообщаться.', reply_markup=standard.standard_keyboard(message.from_user.id))

#Хэндлеры стали мешаться.
@bot.message_handler(func=lambda message: True, content_types=['text', 'contact', 'photo', 'document', 'location'])
def routing(message):
    session = db_connector.get_session()
    try:
        user = session.query(User).filter_by(telegramid=message.from_user.id).first()
        if not user:
            user=User(telegramid=message.from_user.id)
            session.add(user)
            user.operation = Operation()
            session.commit()
        if user.operation is None:
            user.operation = Operation()
            session.commit()
        db_connector.save_to_log(from_who='user', message=message)  # Сохранение входящего сообщения в БД.
        text = utils.text_lower_wo_command(message)
        if not user.active:
            bot.send_message(message.chat.id, 'Вы заблокированы.')
        elif text in ('start', 'help'):
            handle_start_help(message, session, user)
        elif not user.registrationDone or user.operation.current_operation == opRegister:
            register_flow(bot, message, session)
        elif text in admin_functions.admin_commands:
            #Для правильной работы необходим заполненный admin_id в config
            admin_functions.admin_flow(bot, message, session)
        elif text in standard.start_quest_command or user.operation.current_operation == do_quest.opDoQest:
            #do_quest.quest_flow(bot, message, session)
            pass
        elif text in standard.add_quest_command or user.operation.current_operation == add_quest.opAddQest:
            #add_quest.add_quest_flow(bot, message, session)
            pass
        else:
            not_found(message)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


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
