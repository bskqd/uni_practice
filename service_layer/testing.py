from datetime import datetime
from typing import Union, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload

from models import Question, UserTest, UserAnswer, User, Answer
from service_layer.exceptions import NotAllQuestionsAnsweredException, InvalidUsernameException
from service_layer.unit_of_work import AbstractUnitOfWork


class GetUserAnswersService:
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
                joinedload(UserAnswer.question).selectinload(Question.answers), selectinload(UserAnswer.answers)
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
                ).selectinload(
                    UserAnswer.answers
                )
            )
        )


class FinishUserTest:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.users_repo = self.uow.users_repo
        self.questions_repo = self.uow.questions_repo
        self.answers_repo = self.uow.answers_repo
        self.user_tests_repo = self.uow.user_tests_repo
        self.user_answers_repo = self.uow.user_answers_repo

    def __call__(self, username: str, answers: dict[str, Union[str, list[str, ...]]]):
        correct_answers = 0
        all_questions_answered = True
        user_test = self.__get_unfinished_user_test(username)
        for user_answer in user_test.user_answers:
            given_answer = answers.get(str(user_answer.question_id))
            if not given_answer:
                all_questions_answered = False
                continue
            given_answer_ids = (
                [int(given_answer)] if isinstance(given_answer, str) else [int(answer) for answer in given_answer]
            )
            answer_is_correct = False
            if user_answer.question.type == Question.QuestionTypes.SINGLE:
                answer_is_correct = self.__single_choice_answer_is_correct(user_answer, given_answer_ids)
            elif user_answer.question.type == Question.QuestionTypes.MULTI:
                answer_is_correct = self.__multi_choice_answer_is_correct(user_answer, given_answer_ids)
            if answer_is_correct:
                correct_answers += 1
            self.user_answers_repo.update_object(
                user_answer,
                is_correct=answer_is_correct,
                answers=self.answers_repo.get_many(Answer.id.in_(given_answer_ids), fields_to_load=(Answer.id,)),
            )
        if all_questions_answered:
            result = round((correct_answers / len(user_test.user_answers)) * 100)
            self.user_tests_repo.update_object(user_test, result=result, finished_at=datetime.utcnow())
        self.uow.commit()
        if not all_questions_answered:
            raise NotAllQuestionsAnsweredException
        return result

    def __get_unfinished_user_test(self, username: str) -> UserTest:
        user_test = self.user_tests_repo.get_one(
            db_query=select(UserTest).join(User).options(
                selectinload(UserTest.user_answers).joinedload(UserAnswer.question),
                selectinload(UserTest.user_answers).selectinload(UserAnswer.answers),
            ).where(User.username == username, UserTest.result.is_(None),)
        )
        if not user_test:
            raise InvalidUsernameException
        return user_test

    def __single_choice_answer_is_correct(self, user_answer: UserAnswer, given_answer_ids: list[int]) -> bool:
        for answer in user_answer.question.answers:
            if answer.id in given_answer_ids:
                return answer.is_correct
        return False

    def __multi_choice_answer_is_correct(self, user_answer: UserAnswer, given_answer_ids: list[int]) -> bool:
        right_answer_ids = [answer.id for answer in user_answer.question.answers if answer.is_correct]
        return set(right_answer_ids) == set(given_answer_ids)
