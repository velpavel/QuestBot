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
    additional_info_db = Column(String())
    additional_info = {}

    def __repr__(self):
        return '{}: {}. {}'.format(self.user, self.current_operation, self.operation_status)

    def decode_additional(self):
        self.additional_info = json.loads(self.additional_info_db)

    def code_additional(self):
        self.additional_info_db = json.dumps(self.additional_info)


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


def create_all():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_all()
