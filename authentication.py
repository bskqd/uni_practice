import functools
from typing import Callable

from wsgi_application.authentication import AuthenticationError


def authentication_required(request_handler: Callable):
    from wsgi_application.application import Request

    @functools.wraps(request_handler)
    def _authentication_required(request: Request, database_connection, *args, **kwargs):
        if not request.session or not request.session.get('username'):
            raise AuthenticationError
        return request_handler(request, database_connection, *args, **kwargs)

    return _authentication_required
