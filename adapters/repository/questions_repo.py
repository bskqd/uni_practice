import abc

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from adapters.repository.repo import SQLAlchemyRepository
from models import Question


class QuestionsRepositoryABC(SQLAlchemyRepository, abc.ABC):
    @abc.abstractmethod
    def get_questions_for_user_test(self):
        raise NotImplementedError


class QuestionsRepository(QuestionsRepositoryABC):
    def __init__(self, db_session: Session):
        super().__init__(Question, db_session)

    def get_questions_for_user_test(self):
        return self.get_many(db_query=select(Question).order_by(func.random()).limit(3))
