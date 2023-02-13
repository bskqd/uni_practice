from models import User
from service_layer.unit_of_work import AbstractUnitOfWork


class UserLoginService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.users_repo = uow.users_repo

    def __call__(self, username: str) -> bool:
        if self.users_repo.exists(User.username == username):
            return True
        self.users_repo.create(username=username)
        self.uow.commit()
        return True

