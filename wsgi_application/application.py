import logging
from typing import Callable, Type

from wsgi_application.authentication import AuthenticationError
from wsgi_application.database import DatabaseSessionMakerABC, FakeDatabaseSessionMaker
from wsgi_application.logging import get_default_logging_configuration, FakeLogger
from wsgi_application.request import RequestCreator, Request
from wsgi_application.response import ResponseABC, SimpleResponse
from wsgi_application.routing import Router, Route
from wsgi_application.sessions import FilesystemSessionsBackend, SessionsBackendABC


class Application:
    def __init__(self):
        self._routers: list[Router] = []
        self.logging_configuration = get_default_logging_configuration()
        self.loggers = {}
        self.access_logger = self.errors_logger = FakeLogger()
        self.configure_loggers()
        self._authentication_failed_redirect_path = ''
        self.__sessions_backend: SessionsBackendABC = FilesystemSessionsBackend()
        self.__request_creator = RequestCreator(self.__sessions_backend)
        self.__database_session_maker = FakeDatabaseSessionMaker

    def __call__(self, environ: dict, start_response: Callable):
        with self.__database_session_maker() as database_session:
            request = self.__request_creator.create_request(environ)
            try:
                response: ResponseABC = self.handle_request(request, database_session)
            except AuthenticationError:
                self.access_logger.info(f'"{environ["PATH_INFO"]}" - 302')
                self.errors_logger.exception(f'Authentication error after accessing "{environ["PATH_INFO"]}"')
                start_response('302', [('Location', self._authentication_failed_redirect_path)])
                return []
            except Exception:
                self.access_logger.info(f'"{environ["PATH_INFO"]}" - 500')
                self.errors_logger.exception(f'Unexpected error occurred after accessing "{environ["PATH_INFO"]}"')
                start_response('500', [])
                return []
            self.access_logger.info(f'"{environ["PATH_INFO"]}" - {response.status}')
            start_response(str(response.status), response.headers)
            return response.format_response()

    def include_router(self, router: Router):
        self._routers.append(router)

    def configure_loggers(self):
        self.loggers.clear()
        handlers = {}
        for logger_name, logger_data in self.logging_configuration.get('loggers', {}).items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(logger_data.get('level', logging.INFO))
            for handler_name in logger_data.get('handlers', []):
                if handler_name in handlers:
                    handler = handlers[handler_name]
                else:
                    handler_data = self.logging_configuration['handlers'][handler_name].copy()
                    handler_class = handler_data.pop('class')
                    formatter_name = handler_data.pop('formatter', None)
                    handler = handler_class(**handler_data, )
                    if formatter_name:
                        formatter_data = self.logging_configuration['formatters'][formatter_name].copy()
                        formatter_class = formatter_data.pop('class')
                        handler.setFormatter(formatter_class(**formatter_data))
                    handlers[handler_name] = handler
                logger.addHandler(handler)
            self.loggers[logger_name] = logger
        if 'application.access' in self.loggers:
            self.access_logger = self.loggers['application.access']
        if 'application.errors' in self.loggers:
            self.errors_logger = self.loggers['application.errors']

    def set_authentication_failed_redirect_path(self, path: str):
        self._authentication_failed_redirect_path = path

    def set_database_session_maker(self, database_connection_opener: Type[DatabaseSessionMakerABC]):
        self.__database_session_maker = database_connection_opener

    def set_sessions_backend(self, session_backend: SessionsBackendABC):
        self.__sessions_backend = session_backend
        self.__request_creator.sessions_backend = session_backend

    def handle_request(self, request: Request, database_session: DatabaseSessionMakerABC) -> ResponseABC:
        for router in self._routers:
            route: Route = router.get_route(path=request.path)
            if route:
                if request.method not in route.methods:
                    return SimpleResponse(405, 'Method is not allowed')
                return route.handler(request, database_session)
        return SimpleResponse(request, 404, 'Path is not valid')
