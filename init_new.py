# -*- coding: utf-8 -*-
'''Файл для инициализации/установки бота.
Создаёт базу данных, создаёт файл config.ini из шаблона config_skeleton.ini.
Посе запуска необходимо будет внести Token в config.ini

PaVel 09.2016
'''
import sqlite3
import configparser
import shutil, os

if not os.path.exists(r'config.ini'):
    shutil.copy(r'config_skeleton.ini', r'config.ini')

config = configparser.ConfigParser()
config.read('config.ini')
SQLITEDB = config['DB']['Dbfile']

sql = '''--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Таблица: user_operation
CREATE TABLE user_operation (Telegramid INTEGER UNIQUE NOT NULL PRIMARY KEY REFERENCES users (Telegramid), current_operation TEXT, operation_status, additional_info TEXT);

-- Таблица: log
CREATE TABLE log (datetime DATETIME, from_who, user_id, msg_text TEXT, operation TEXT, status, additional_info, function, comment TEXT);

-- Таблица: users
CREATE TABLE users (Telegramid INTEGER PRIMARY KEY NOT NULL, Phone INTEGER, Name VARCHAR (50), Email VARCHAR (50), RegistrationDone BOOLEAN DEFAULT (0) NOT NULL, RegistrationDate DATETIME, Active BOOLEAN DEFAULT (1));

-- Таблица: quest_answer_details
CREATE TABLE quest_answer_details (id INTEGER PRIMARY KEY AUTOINCREMENT, answer_header_id INTEGER REFERENCES quest_quest (id), task_id INTEGER REFERENCES quest_quest (id), date_start DATETIME, date_end DATETIME, count_answers);

-- Таблица: quest_task
CREATE TABLE quest_task (id INTEGER PRIMARY KEY AUTOINCREMENT, quest_id INTEGER REFERENCES quest_quest (ID), sequence INTEGER, description, photo, answer_type, correct_answer VARCHAR, Active BOOLEAN DEFAULT (1));

-- Таблица: quest_answer_header
CREATE TABLE quest_answer_header (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id REFERENCES users (Telegramid), quest_id INTEGER REFERENCES quest_quest (ID), current_question INTEGER REFERENCES quest_task (id), done BOOLEAN DEFAULT (0), canceled BOOLEAN DEFAULT (0), date_start DATETIME, date_end DATETIME);

-- Таблица: quest_quest
CREATE TABLE quest_quest (ID INTEGER PRIMARY KEY AUTOINCREMENT, Name, Author, Description, Photo, Start_location, Type, Active BOOLEAN DEFAULT (1));

-- Индекс: idx_user_operation_telegramid
CREATE UNIQUE INDEX idx_user_operation_telegramid ON user_operation (Telegramid);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
'''

if not os.path.exists(SQLITEDB):
    con = sqlite3.connect(SQLITEDB)
    cur = con.cursor()
    cur.executescript(sql)
    con.commit()
    con.close()