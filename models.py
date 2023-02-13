from enum import Enum

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func, null
from sqlalchemy.orm import relationship

from database.base import Base

__all__ = ['User', 'UserTest', 'UserAnswer', 'Question', 'Answer']


class IdFieldMixin(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)


class CreatedAtMixin(Base):
    __abstract__ = True

    created_at = Column(DateTime, default=func.now())


class User(IdFieldMixin):
    __tablename__ = 'users'

    username = Column(String, unique=True, nullable=False)

    tests = relationship('UserTest', back_populates='user', cascade='all, delete')


class UserTest(IdFieldMixin, CreatedAtMixin):
    __tablename__ = 'user_tests'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=False)
    result = Column(Integer, nullable=True)

    user = relationship('User', back_populates='tests')
    user_answers = relationship('UserAnswer', back_populates='user_test', cascade='all, delete')


class UserAnswer(IdFieldMixin, CreatedAtMixin):
    __tablename__ = 'user_answers'

    user_test_id = Column(Integer, ForeignKey('user_tests.id', ondelete='CASCADE'), index=True, nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), index=True, nullable=False)
    # TODO: rework into m2m
    answer_id = Column(Integer, ForeignKey('answers.id'), index=True, nullable=True)
    answered_at = Column(DateTime, default=None, onupdate=func.now())
    is_correct = Column(Boolean, default=False, nullable=False)

    user_test = relationship('UserTest', back_populates='user_answers')
    question = relationship('Question', back_populates='user_answers')
    answer = relationship('Answer', back_populates='user_answers')


class Question(IdFieldMixin):
    __tablename__ = 'questions'

    class QuestionTypes(str, Enum):
        SINGLE = 'single'
        MULTI = 'multi'

    text = Column(String, nullable=False)
    type = Column(String, nullable=False, default=QuestionTypes.SINGLE)

    answers = relationship('Answer', back_populates='question', cascade='all, delete')
    user_answers = relationship('UserAnswer', back_populates='question')


class Answer(IdFieldMixin):
    __tablename__ = 'answers'

    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), index=True, nullable=False)
    is_right = Column(Boolean, nullable=False, default=False)
    text = Column(String, nullable=False)

    question = relationship('Question', back_populates='answers')
    user_answers = relationship('UserAnswer', back_populates='answer')
