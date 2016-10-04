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

sql = '''PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Таблица: users - информация о пользователях
DROP TABLE IF EXISTS users;
CREATE TABLE users (Telegramid INTEGER PRIMARY KEY NOT NULL, Phone INTEGER, Name VARCHAR (50), Email VARCHAR (50), RegistrationDone BOOLEAN DEFAULT (0) NOT NULL, RegistrationDate DATETIME);

-- Таблица: user_operation - сохраняется текущий статус для каждого пользователя
DROP TABLE IF EXISTS user_operation;
CREATE TABLE user_operation (Telegramid INTEGER UNIQUE NOT NULL PRIMARY KEY, current_operation TEXT, operation_status, additional_info TEXT);

-- Индекс: idx_user_operation_telegramid
DROP INDEX IF EXISTS idx_user_operation_telegramid;
CREATE UNIQUE INDEX idx_user_operation_telegramid ON user_operation (Telegramid);

-- Таблица: log
DROP TABLE IF EXISTS log;
CREATE TABLE log (datetime DATETIME, from_who, user_id, msg_text TEXT, operation TEXT, status, additional_info, function, comment TEXT);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;'''

if not os.path.exists(SQLITEDB):
    con = sqlite3.connect(SQLITEDB)
    cur = con.cursor()
    cur.executescript(sql)
    con.commit()
    con.close()