import abc
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Union, Optional

from wsgi_application.request import Request


class ResponseABC(abc.ABC):
    def __init__(self, request: Request, status: Union[str, int], content_type: str):
        self.status = status
        self.__headers: list[tuple, ...] = []
        self.__headers.append(('Content-Type', content_type))
        self.__request: Request = request

    @abc.abstractmethod
    def format_response(self):
        pass

    @property
    def headers(self) -> list[tuple, ...]:
        return deepcopy(self.__headers)

    def add_header(self, key: str, value: str):
        if key.lower() == 'content-type' or key.lower() == 'set-cookie':
            return
        self.__headers.append((key, value))

    def set_cookie_header(self, key: str, value: str, seconds: int = 600 * 600):
        if key.lower() == 'session':
            return
        self.__set_cookie_header(key, value, seconds)

    def set_session(self, session_data: dict, session_id: Optional[str] = None):
        if session_id:
            self.__set_cookie_header('session', session_id)
        elif not self.__request.session_id:
            session_id = self.__request.sessions_backend.generate_session_id()
            self.__set_cookie_header('session', session_id)
        session_id = session_id or self.__request.session_id
        self.__request.sessions_backend.write_session_data(session_id, session_data)

    def __set_cookie_header(self, key: str, value: str, seconds: int = 600 * 600):
        dt = (datetime.now() + timedelta(seconds=seconds)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        self.__headers.append(('Set-Cookie', f'{key}={value}; Expires={dt}; Max-Age={seconds}; Path=/'))


class SimpleResponse(ResponseABC):
    def __init__(self, request: Request, status: Union[str, int], text: str):
        super().__init__(request, status, 'text/html')
        self.text = text

    def format_response(self):
        return [self.text.encode()]
