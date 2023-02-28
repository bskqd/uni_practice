import abc

from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload, Session

from adapters.repository.repo import SQLAlchemyRepository
from models import UserTest, UserAnswer, Question


class UserAnswersRepositoryABC(SQLAlchemyRepository, abc.ABC):
    @abc.abstractmethod
    def get_user_answers_for_test(self, user_test_id: int) -> list[UserAnswer]:
        raise NotImplementedError


class UserAnswersRepository(UserAnswersRepositoryABC):
    def __init__(self, db_session: Session):
        super().__init__(UserAnswer, db_session)

    def get_user_answers_for_test(self, user_test_id: int) -> list[UserAnswer]:
        return self.get_many(
            db_query=select(
                UserAnswer
            ).join(
                UserAnswer.user_test
            ).where(
                UserTest.id == user_test_id
            ).options(
                joinedload(UserAnswer.question).selectinload(Question.answers),
                selectinload(UserAnswer.answers)
            )
        )
