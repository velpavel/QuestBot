# -*- coding: utf-8 -*-
'''Файл для инициализации/установки бота.
Создаёт базу данных, создаёт файл config.ini из шаблона config_skeleton.ini.
Посе запуска необходимо будет внести Token в config.ini

PaVel 09.2016
'''
import models
import shutil, os

if not os.path.exists(r'config.ini'):
    shutil.copy(r'config_skeleton.ini', r'config.ini')

models.create_all()