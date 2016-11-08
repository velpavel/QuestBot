# -*- coding: utf-8 -*-
'''Модели

PaVel 10.2016
'''

from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime, Boolean, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
import configparser, enum, json

config = configparser.ConfigParser()
config.read('config.ini')
Base = declarative_base()
base_url = 'sqlite:///{}'.format(config['DB']['Dbfile'])

class User(Base):
    __tablename__ = 'user'
    telegramid = Column(Integer, primary_key=True, index=True)
    phone = Column(String(200))
    name = Column(String(255))
    email = Column(String(200))
    registrationDone = Column(Boolean(), default=False)
    registrationDate = Column(Date)
    active = Column(Boolean, default=False)

    def __repr__(self):
        return self.name


class Operation(Base):
    __tablename__ = 'user_operation'
    telegramid = Column(Integer, ForeignKey('user.telegramid'), primary_key=True, index=True)
    user = relationship(User, backref=backref("opertion", uselist=False))
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

##Quest###############

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

class Task_types(enum.Enum):
    text = 'txt'
    digit = 'dig'
    geo = 'geo'

class Task(Base):
    __tablename__ = 'quest_task'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    quest_id = Column(Integer, ForeignKey('quest.id'), index=True)
    sequence = Column(Integer)
    description = Column(String(255))
    photo = Column(String())
    answer_type = Column(Enum(Task_types))
    correct_answer_db = Column(String())
    active = Column(Boolean, default=False)
    correct_answer = {}

    def __repr__(self):
        return self.description

    def get_answ(self):
        if self.answer_type == Task_types.text: self.correct_answer=self.correct_answer_db
        elif self.answer_type == Task_types.digit: self.correct_answer=float(self.correct_answer_db)
        elif self.answer_type == Task_types.geo:
            correct_answer_l = json.loads(self.correct_answer_db)
            self.correct_answer['lat'] = correct_answer_l.get('lat')
            self.correct_answer['long'] = correct_answer_l.get('long')
            self.correct_answer['accur'] = correct_answer_l.get('accur', 50)
            self.correct_answer['hint_meters'] = correct_answer_l.get('hint_meters', False)
        return self.correct_answer

    def save_answ(self):
        if self.answer_type == Task_types.text: self.correct_answer_db=self.correct_answer
        elif self.answer_type == Task_types.digit: self.correct_answer_db=str(self.correct_answer)
        elif self.answer_type == Task_types.geo: self.correct_answer_db = json.dumps(self.correct_answer)


if __name__ == '__main__':
    engine = create_engine(base_url)
    Base.metadata.create_all(engine)