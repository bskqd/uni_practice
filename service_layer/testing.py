from datetime import datetime
from typing import Union

from models import Question, UserAnswer, User, Answer
from service_layer.exceptions import NotAllQuestionsAnsweredException, NoUnfinishedUserTestException
from service_layer.unit_of_work import AbstractUnitOfWork


class GetUserTestAnswers:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.users_repo = self.uow.users_repo
        self.questions_repo = self.uow.questions_repo
        self.user_tests_repo = self.uow.user_tests_repo
        self.user_answers_repo = self.uow.user_answers_repo

    def __call__(self, username: str) -> list[UserAnswer]:
        unfinished_user_test = self.user_tests_repo.get_unfinished_user_test(
            username=username, load_relationships=False,
        )
        if not unfinished_user_test:
            user = self.users_repo.get_one(User.username == username)
            unfinished_user_test = self.user_tests_repo.create(user_id=user.id)
            self.user_tests_repo.flush()
            self.user_tests_repo.refresh(unfinished_user_test)
            questions = self.questions_repo.get_questions_for_user_test()
            for question in questions:
                self.user_answers_repo.create(user_test_id=unfinished_user_test.id, question_id=question.id)
            self.uow.commit()
        return self.user_answers_repo.get_user_answers_for_test(user_test_id=unfinished_user_test.id)


class FinishUserTest:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.answers_repo = self.uow.answers_repo
        self.user_tests_repo = self.uow.user_tests_repo
        self.user_answers_repo = self.uow.user_answers_repo

    def __call__(self, username: str, answers: dict[str, Union[str, list[str, ...]]]):
        unfinished_user_test = self.user_tests_repo.get_unfinished_user_test(username=username)
        correct_answers = 0
        all_questions_answered = True
        if not unfinished_user_test:
            raise NoUnfinishedUserTestException
        for user_answer in unfinished_user_test.user_answers:
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
        if not all_questions_answered:
            self.uow.commit()
            raise NotAllQuestionsAnsweredException
        result = round((correct_answers / len(unfinished_user_test.user_answers)) * 100)
        self.user_tests_repo.update_object(unfinished_user_test, result=result, finished_at=datetime.utcnow())
        self.uow.commit()
        return result

    def __single_choice_answer_is_correct(self, user_answer: UserAnswer, given_answer_ids: list[int]) -> bool:
        for answer in user_answer.question.answers:
            if answer.id in given_answer_ids:
                return answer.is_correct
        return False

    def __multi_choice_answer_is_correct(self, user_answer: UserAnswer, given_answer_ids: list[int]) -> bool:
        right_answer_ids = [answer.id for answer in user_answer.question.answers if answer.is_correct]
        return set(right_answer_ids) == set(given_answer_ids)
