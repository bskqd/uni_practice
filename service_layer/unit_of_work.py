from __future__ import annotations

from typing import Optional

from adapters.repository import AbstractRepository
import abc


class AbstractUnitOfWork(abc.ABC):
    users_repo: Optional[AbstractRepository]
    questions_repo: Optional[AbstractRepository]
    answers_repo: Optional[AbstractRepository]
    user_tests_repo: Optional[AbstractRepository]
    user_answers_repo: Optional[AbstractRepository]

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(
            self,
            sessionmaker,
            users_repo: Optional[AbstractRepository] = None,
            questions_repo: Optional[AbstractRepository] = None,
            answers_repo: Optional[AbstractRepository] = None,
            user_tests_repo: Optional[AbstractRepository] = None,
            user_answers_repo: Optional[AbstractRepository] = None,
    ):
        self.sessionmaker = sessionmaker
        self.__repos = []
        self.users_repo = self.__add_repo(users_repo)
        self.questions_repo = self.__add_repo(questions_repo)
        self.answers_repo = self.__add_repo(answers_repo)
        self.user_tests_repo = self.__add_repo(user_tests_repo)
        self.user_answers_repo = self.__add_repo(user_answers_repo)

    def __add_repo(self, repo: Optional[AbstractRepository]) -> AbstractRepository:
        if repo:
            self.__repos.append(repo)
        return repo

    def __enter__(self):
        if hasattr(self, '__session'):
            return super().__enter__()
        self.__session = self.sessionmaker()
        for repo in self.__repos:
            repo.set_db_session(self.__session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.__session.close()

    def _commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()
