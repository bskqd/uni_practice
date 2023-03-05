import abc
from dataclasses import dataclass
from typing import Union, Any
from urllib import parse

from wsgi_application.sessions import SessionsBackendABC, FilesystemSessionsBackend


@dataclass(frozen=True)
class Request:
    path: str
    method: str
    cookies: dict
    session_id: str
    session: dict
    sessions_backend: SessionsBackendABC
    body: Any
    query_params: dict[str, Union[str, list[str]]]


class BodyParser(abc.ABC):
    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class FormUrlencodedBodyParser(BodyParser):
    def __call__(self, environ: dict) -> dict[str, Union[str, list[str]]]:
        body = parse.parse_qs(environ['wsgi.input'].read().decode(), keep_blank_values=True)
        for k, v in body.items():
            if isinstance(v, list) and len(v) == 1:
                body[k] = v[0]
        return body


class RequestCreator:
    def __init__(self, sessions_backend: SessionsBackendABC = FilesystemSessionsBackend()):
        self.__default_body_parser = FormUrlencodedBodyParser()
        self.__body_parsers: dict[str, BodyParser] = {'application/x-www-form-urlencoded': self.__default_body_parser}
        self.__sessions_backend = sessions_backend

    @property
    def sessions_backend(self) -> SessionsBackendABC:
        return self.__sessions_backend

    @sessions_backend.setter
    def sessions_backend(self, session_backend: SessionsBackendABC):
        self.__sessions_backend = session_backend

    def create_request(self, environ: dict) -> Request:
        cookies = self.__parse_cookies(environ.get('HTTP_COOKIE', ''))
        session_id = cookies.get('session', '')
        session = self.__sessions_backend.get_session_data(session_id)
        return Request(
            path=environ['PATH_INFO'],
            method=environ['REQUEST_METHOD'],
            cookies=cookies,
            session_id=session_id,
            session=session,
            sessions_backend=self.sessions_backend,
            body=self.__parse_body(environ),
            query_params=self.__parse_query_params(environ),
        )

    def __parse_body(self, environ: dict) -> dict:
        content_type = environ.get('CONTENT_TYPE', 'application/x-www-form-urlencoded')
        parser = self.__body_parsers.get(content_type, self.__default_body_parser)
        return parser(environ)

    def __parse_query_params(self, environ: dict) -> dict[str, list[str]]:
        query_params = parse.parse_qs(environ['QUERY_STRING'])
        for k, v in query_params.items():
            if isinstance(v, list) and len(v) == 1:
                query_params[k] = v[0]
        return query_params

    def __parse_cookies(self, cookies_string: str) -> dict:
        cookies = {}
        if not cookies_string:
            return cookies
        for cookie in cookies_string.split('; '):
            cookie = cookie.split('=')
            cookies[cookie[0]] = parse.unquote(cookie[1])
        return cookies
