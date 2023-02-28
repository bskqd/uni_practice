import abc

from sqlalchemy.orm import Session

from adapters.repository.repo import SQLAlchemyRepository
from models import Answer


class AnswersRepositoryABC(SQLAlchemyRepository, abc.ABC):
    pass


class AnswersRepository(AnswersRepositoryABC):
    def __init__(self, db_session: Session):
        super().__init__(Answer, db_session)
