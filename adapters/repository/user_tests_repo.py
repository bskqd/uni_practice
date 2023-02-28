import abc
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload, Session, contains_eager

from adapters.repository.repo import SQLAlchemyRepository
from models import UserTest, User, UserAnswer


class UserTestsRepositoryABC(SQLAlchemyRepository, abc.ABC):
    @abc.abstractmethod
    def get_unfinished_user_test(self, username: str, load_relationships: bool = True) -> Optional[UserTest]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_tests_by_user(self, username: str) -> list[UserTest]:
        raise NotImplementedError


class UserTestsRepository(UserTestsRepositoryABC):
    def __init__(self, db_session: Session):
        super().__init__(UserTest, db_session)

    def get_unfinished_user_test(self, username: str, load_relationships: bool = True) -> Optional[UserTest]:
        db_query = select(
            UserTest
        ).join(
            UserTest.user,
        ).where(
            User.username == username,
            UserTest.result.is_(None),
        )
        if load_relationships:
            db_query = db_query.options(
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
        return self.get_one(db_query=db_query)

    def get_user_tests_by_user(self, username: str) -> list[UserTest]:
        return self.get_many(
            db_query=select(
                UserTest
            ).join(
                UserTest.user
            ).options(
                contains_eager(UserTest.user)
            ).where(User.username == username),
            fields_to_load=(UserTest.result, UserTest.finished_at),
        )
