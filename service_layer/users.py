from models import User, UserTest
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


class GetUserTestsService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.user_tests_repo = self.uow.user_tests_repo

    def __call__(self, username: str) -> list[UserTest]:
        return self.user_tests_repo.get_many(fields_to_load=(UserTest.result, UserTest.finished_at))

