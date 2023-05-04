from inspect import signature
from typing import Callable, Type

from wsgi_application.authentication import AuthenticationError
from wsgi_application.database import DatabaseSessionMakerABC, FakeDatabaseSessionMaker
from wsgi_application.logging import Logger, get_default_logging_configuration, LoggerABC
from wsgi_application.request import RequestCreator, Request
from wsgi_application.response import ResponseABC, SimpleResponse
from wsgi_application.routing import Router, Route
from wsgi_application.sessions import FilesystemSessionsBackend, SessionsBackendABC


class Application:
    def __init__(self):
        self._routers: list[Router] = []
        self.logger = Logger(get_default_logging_configuration())
        self.__dependencies: dict[Callable, Callable] = {LoggerABC: lambda: self.logger}
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
                self.logger.exception(f'Authentication error after accessing "{environ["PATH_INFO"]}"')
                start_response('302', [('Location', self._authentication_failed_redirect_path)])
                return []
            except Exception:
                self.logger.exception(f'Unexpected error occurred after accessing "{environ["PATH_INFO"]}"')
                start_response('500', [])
                return []
            start_response(str(response.status), response.headers)
            return response.format_response()

    def include_router(self, router: Router):
        self._routers.append(router)

    def change_logger_configuration(self, configuration: dict):
        self.logger.configuration = configuration

    def override_dependencies(self, dependencies: dict[Callable, Callable]):
        self.__dependencies.update(dependencies)

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
                    return SimpleResponse(request, 405, 'Method is not allowed')
                return self.inject_dependencies(route.handler, request, database_session)
        return SimpleResponse(request, 404, 'Path is not valid')

    def inject_dependencies(self, handler: Callable, *args, **kwargs):
        for param_name, param in signature(handler).parameters.items():
            if dependency := self.__dependencies.get(param.annotation):
                kwargs[param_name] = dependency()
        return handler(*args, **kwargs)
