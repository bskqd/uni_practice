from typing import Callable

from service_layer.unit_of_work import SqlAlchemyUnitOfWork
from wsgi_application.request import Request


def provide_uow(func: Callable):
    def _provide_uow(request: Request, database_session):
        uow = SqlAlchemyUnitOfWork(database_session)
        with uow:
            return func(request, uow)

    return _provide_uow
