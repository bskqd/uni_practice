import json
from datetime import datetime
from typing import Union, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload

from models import Question, UserTest, UserAnswer, User
from service_layer.exceptions import NotAllQuestionsAnsweredException, InvalidUsernameException
from service_layer.unit_of_work import AbstractUnitOfWork


class GetQuestionsService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.users_repo = self.uow.users_repo
        self.questions_repo = self.uow.questions_repo
        self.user_tests_repo = self.uow.user_tests_repo
        self.user_answers_repo = self.uow.user_answers_repo

    def __call__(self, username: str) -> list[UserAnswer]:
        user = self.users_repo.get_one(User.username == username)
        if not user:
            return []
        unfinished_user_test = self.__get_unfinished_user_test(username)
        if unfinished_user_test:
            return unfinished_user_test.user_answers
        user_test = self.user_tests_repo.create(user_id=user.id)
        self.user_tests_repo.flush()
        self.user_tests_repo.refresh(user_test)
        questions = self.questions_repo.get_many(db_query=select(Question).order_by(func.random()).limit(3))
        for question in questions:
            self.user_answers_repo.create(user_test_id=user_test.id, question_id=question.id)
        self.uow.commit()
        return self.user_answers_repo.get_many(
            db_query=select(UserAnswer).join(UserAnswer.user_test).where(UserTest.id == user_test.id).options(
                joinedload(UserAnswer.question).selectinload(Question.answers), joinedload(UserAnswer.answer)
            )
        )

    def __get_unfinished_user_test(self, username: str) -> Optional[UserTest]:
        return self.user_tests_repo.get_one(
            db_query=select(
                UserTest
            ).join(
                UserTest.user,
            ).where(
                User.username == username,
                UserTest.result.is_(None),
            ).options(
                selectinload(
                    UserTest.user_answers
                ).joinedload(
                    UserAnswer.question
                ),
                selectinload(
                    UserTest.user_answers
                ).joinedload(
                    UserAnswer.answer
                )
            )
        )


def process_answers(username: str, answers: dict[str, Union[str, list[str, ...]]]) -> int:
    if not username:
        raise InvalidUsernameException
    with open('questions.json', 'r') as questions_file:
        questions = json.load(questions_file)
    correct_answers = 0
    for question_id, question_data in questions.items():
        try:
            given_answer = answers[question_id]
        except KeyError:
            raise NotAllQuestionsAnsweredException
        if given_answer == question_data['right_answer_id']:
            correct_answers += 1
    result = round((correct_answers / len(questions)) * 100)
    update_user_results(username, result)
    return result


def update_user_results(username: str, result: int):
    with open('user_results.json', 'r') as f:
        try:
            user_results = json.load(f)
        except json.JSONDecodeError:
            user_results = {}
    user_results.setdefault(username, []).append({'result': result, 'datetime': str(datetime.now())})
    with open('user_results.json', 'w') as f:
        json.dump(user_results, f)
