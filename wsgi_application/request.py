import abc
import json
from dataclasses import dataclass
from typing import Union, Any
from urllib import parse


@dataclass
class Request:
    path: str
    method: str
    cookies: dict
    session: dict
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
    def __init__(self):
        self.__default_body_parser = FormUrlencodedBodyParser()
        self.__body_parsers: dict[str, BodyParser] = {'application/x-www-form-urlencoded': self.__default_body_parser}

    def create_request(self, environ: dict) -> Request:
        cookies = self.__parse_cookies(environ.get('HTTP_COOKIE', ''))
        session = self.__load_session(cookies.get('session', ''))
        return Request(
            path=environ['PATH_INFO'],
            method=environ['REQUEST_METHOD'],
            cookies=cookies,
            session=session,
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

    def __load_session(self, session_id: str) -> dict:
        with open('sessions.json', 'r') as f:
            sessions_data = json.load(f)
        session_data = sessions_data.get(session_id)
        if not session_data:
            return {}
        return json.loads(session_data)
