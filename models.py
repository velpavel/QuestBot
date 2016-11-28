# -*- coding: utf-8 -*-
'''Модели

PaVel 10.2016
'''

from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime, Boolean, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import create_engine, event
import configparser, enum, json
from sqlalchemy.ext.hybrid import hybrid_property

config = configparser.ConfigParser()
config.read('config.ini')
Base = declarative_base()
dialect = config['DB']['Dialect']
base_url = ''
if dialect == 'sqlite':
    base_url = 'sqlite:///{}'.format(config['DB']['Dbpath'])
else:
    driver = config['DB'].get('Driver')
    username = config['DB'].get('Driver')
    password = config['DB'].get('Driver')
    dbpath = config['DB'].get('Driver')
    if driver: driver = '+' + driver
    # dialect+driver://username:password@host:port/database
    base_url = '{}{}://{}:{}@{}'.format(dialect, driver, username, password, dbpath)
engine = create_engine(base_url)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'user'
    telegramid = Column(Integer, primary_key=True, index=True)
    phone = Column(String(200))
    name = Column(String(255))
    email = Column(String(200))
    registrationDone = Column(Boolean(), default=False)
    registrationDate = Column(DateTime)
    active = Column(Boolean, default=True)

    def __repr__(self):
        return self.name


class Operation(Base):
    __tablename__ = 'user_operation'
    telegramid = Column(Integer, ForeignKey('user.telegramid'), primary_key=True, index=True)
    user = relationship(User, backref=backref("operation", uselist=False))
    current_operation = Column(String(50))
    operation_status = Column(String(50))
    additional_info = Column(String())

    def __repr__(self):
        return '{}: {}. {}'.format(self.user, self.current_operation, self.operation_status)


class Log(Base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    datetime = Column(DateTime)
    from_who = Column(String(50))
    user_id = Column(Integer, ForeignKey('user.telegramid'), index=True)
    user = relationship(User)
    msg_type = Column(String(50))
    msg_text = Column(String())
    operation = Column(String(50))
    status = Column(String(50))
    additional_info = Column(String())
    function = Column(String(50))
    comment = Column(String())

    def __repr__(self):
        return '{} {}: {}. {}'.format(self.datetime, self.user, self.operation_status, self.msg_text, self.function)


# Quest###############

class Quest(Base):
    __tablename__ = 'quest_quest'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(50))
    description = Column(String(255))
    author_id = Column(Integer, ForeignKey('user.telegramid'), index=True)
    author = relationship(User)
    photo = Column(String())
    start_location_lat = Column(Float)
    start_location_long = Column(Float)
    active = Column(Boolean, default=False)

    def __repr__(self):
        return self.name


class TaskTypes(enum.Enum):
    text = 'txt'
    digit = 'dig'
    geo = 'geo'


class Task(Base):
    __tablename__ = 'quest_task'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    quest_id = Column(Integer, ForeignKey('quest_quest.id'), index=True)
    sequence = Column(Integer)
    description = Column(String(255))
    photo = Column(String())
    # answer_type = Column(Enum(TaskTypes))
    # correct_answer_db = Column(String())
    # correct_answer = {}
    active = Column(Boolean, default=False)

    def __repr__(self):
        return self.description

    # @History
    # correct_answer хранился в json. Это позволяло хранить кучк параметров т.ч. для geo без изменения бд.
    # Разнйо степени кривости были решения через
    # @hybrid_property @correct_answer_value.setter - виртуальные атрибуты.
    # работает, но для каждого создавть новый. getter и setter - некрасиво.
    # events - при изменении объектов в словаре не считается измененим. И для setter и для before_update
    # @event.listens_for(Task, 'load')
    # def task_on_load(target, context):
    #     print("on load!")
    #     target.get_answ()
    # Поискать другое решение. С заменой get и save стнадратных. Чтобы получать словарь.
    # На текущий момент проблема словаря в том, что изменение в нём не вызывает setter (т.к. ссылка на словарь не меняется)
    #
    # @hybrid_property
    # def correct_answer_value(self):
    #     if self.answer_type == TaskTypes.text: _correct_answer=self.correct_answer_db
    #     elif self.answer_type == TaskTypes.digit: _correct_answer=float(self.correct_answer_db)
    #     elif self.answer_type == TaskTypes.geo: _correct_answer=None
    #     return _correct_answer
    #
    # @correct_answer_value.setter
    # def correct_answer_value(self, correct_answer_value):
    #     self.save_answ(correct_answer_value=correct_answer_value)
    #
    # @hybrid_property
    # def correct_answer_lat(self):
    #     return json.loads(self.correct_answer_db).get('lat')
    #
    # @correct_answer_lat.setter
    # def correct_answer_lat(self, correct_answer_lat):
    #     self.save_answ(lat=correct_answer_lat)
    #
    # @hybrid_property
    # def correct_answer_long(self):
    #     return json.loads(self.correct_answer_db).get('long')
    #
    # @correct_answer_long.setter
    # def correct_answer_long(self, correct_answer_long):
    #     self.save_answ(long=correct_answer_long)
    #
    # @hybrid_property
    # def correct_answer_accur(self):
    #     return json.loads(self.correct_answer_db).get('accur')
    #
    # @correct_answer_accur.setter
    # def correct_answer_accur(self, correct_answer_accur):
    #     self.save_answ(accur=correct_answer_accur)
    #
    # @hybrid_property
    # def correct_answer_hint(self):
    #     return json.loads(self.correct_answer_db).get('hint_meters')
    #
    # @correct_answer_hint.setter
    # def correct_answer_hint(self, correct_answer_hint):
    #     self.save_answ(hint_meters=correct_answer_hint)

    # def get_answ(self):
    #     if self.answer_type == TaskTypes.text:
    #         self.correct_answer = self.correct_answer_db
    #     elif self.answer_type == TaskTypes.digit:
    #         self.correct_answer = float(self.correct_answer_db)
    #     elif self.answer_type == TaskTypes.geo:
    #         correct_answer_l = json.loads(self.correct_answer_db)
    #         self.correct_answer['lat'] = correct_answer_l.get('lat')
    #         self.correct_answer['long'] = correct_answer_l.get('long')
    #         self.correct_answer['accur'] = correct_answer_l.get('accur', 50)
    #         self.correct_answer['hint_meters'] = correct_answer_l.get('hint_meters', False)
    #     return self.correct_answer

    # def save_answ(self):
    #     if self.answer_type == TaskTypes.text:
    #         self.correct_answer_db = self.correct_answer
    #     elif self.answer_type == TaskTypes.digit:
    #         self.correct_answer_db = str(self.correct_answer)
    #     elif self.answer_type == TaskTypes.geo:
    #         self.correct_answer_db = json.dumps(self.correct_answer)

    #
    # def save_answ(self, **kwargs):
    #     if self.answer_type == TaskTypes.text: self.correct_answer_db=self.correct_answer
    #     elif self.answer_type == TaskTypes.digit: self.correct_answer_db=str(self.correct_answer)
    #     elif self.answer_type == TaskTypes.geo:
    #         correct_answer={}
    #         correct_answer['lat'] = self.correct_answer_lat
    #         correct_answer['long'] = self.correct_answer_long
    #         correct_answer['accur'] = self.correct_answer_accur
    #         correct_answer['hint_meters'] = self.correct_answer_hint
    #         for key in kwargs:
    #             correct_answer[key] = kwargs[key]
    #         self.correct_answer_db = json.dumps(correct_answer)
#
#
# @event.listens_for(Task, 'load')
# def task_on_load(target, context):
#     print("on load!")
#     target.get_answ()
#
#
# @event.listens_for(Task, 'before_insert')
# @event.listens_for(Task, 'before_update')
# def task_on_save(mapper, connection, target):
#     print("on save!")
#     target.save_answ()


class CorrectAnswer(Base):
    __tablename__ = 'quest_answer'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    task_id = Column(Integer, ForeignKey('quest_task.id'), index=True)
    task = relationship(Task, backref=backref("answers"))
    answer_type = Column(Enum(TaskTypes))
    answer_value = Column(String())
    latitude = Column(Float)
    longitude = Column(Float)
    accuracy = Column(Integer)
    hint = Column(String())
    active = Column(Boolean, default=True)

    def __repr__(self):
        return '{}: {}'.format(self.answer_type, self.answer_value)

if __name__ == '__main__':
    Base.metadata.create_all(engine)
