import functools
from typing import Callable

from service_layer.unit_of_work import SqlAlchemyUnitOfWork
from wsgi_application.request import Request


def provide_uow(func: Callable):
    @functools.wraps(func)
    def _provide_uow(request: Request, database_session, *args, **kwargs):
        uow = SqlAlchemyUnitOfWork(database_session)
        with uow:
            return func(request, uow, *args, **kwargs)

    return _provide_uow
