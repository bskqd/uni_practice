import abc

from sqlalchemy.orm import Session

from adapters.repository.repo import SQLAlchemyRepository
from models import User


class UsersRepositoryABC(SQLAlchemyRepository, abc.ABC):
    pass


class UsersRepository(UsersRepositoryABC):
    def __init__(self, db_session: Session):
        super().__init__(User, db_session)
