from __future__ import annotations

import abc

from sqlalchemy.orm import Session

from adapters.repository.answers_repo import AnswersRepositoryABC, AnswersRepository
from adapters.repository.questions_repo import QuestionsRepositoryABC, QuestionsRepository
from adapters.repository.user_answers_repo import UserAnswersRepository, UserAnswersRepositoryABC
from adapters.repository.user_tests_repo import UserTestsRepository, UserTestsRepositoryABC
from adapters.repository.users_repo import UsersRepositoryABC, UsersRepository


class AbstractUnitOfWork(abc.ABC):
    users_repo: UsersRepositoryABC
    questions_repo: QuestionsRepositoryABC
    answers_repo: AnswersRepositoryABC
    user_tests_repo: UserTestsRepositoryABC
    user_answers_repo: UserAnswersRepositoryABC

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: Session):
        self.__session = session
        self.users_repo = UsersRepository(session)
        self.questions_repo = QuestionsRepository(session)
        self.answers_repo = AnswersRepository(session)
        self.user_tests_repo = UserTestsRepository(session)
        self.user_answers_repo = UserAnswersRepository(session)

    def __exit__(self, *args):
        super().__exit__(*args)

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()
