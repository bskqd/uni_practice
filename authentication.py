from typing import Callable

from wsgi_application.authentication import AuthenticationError


def authentication_required(request_handler: Callable):
    from wsgi_application.application import Request

    def _authentication_required(request: Request, database_connection):
        if not request.session or not request.session.get('username'):
            raise AuthenticationError
        return request_handler(request, database_connection)

    return _authentication_required
