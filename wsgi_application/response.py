import abc
import json
import uuid
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Union


class ResponseABC(abc.ABC):
    def __init__(self, status: Union[str, int], content_type: str):
        self.status = status
        self.__headers: list[tuple, ...] = []
        self.__headers.append(('Content-Type', content_type))

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

    def set_session(self, session_data: dict):
        session_id = uuid.uuid4().hex
        self.__set_cookie_header('session', session_id)
        with open('sessions.json', 'r') as f:
            sessions_data = json.load(f)
        sessions_data[session_id] = json.dumps(session_data)
        with open('sessions.json', 'w') as f:
            json.dump(sessions_data, f)

    def __set_cookie_header(self, key: str, value: str, seconds: int = 600 * 600):
        dt = (datetime.now() + timedelta(seconds=seconds)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        self.__headers.append(('Set-Cookie', f'{key}={value}; Expires={dt}; Max-Age={seconds}; Path=/'))


class SimpleResponse(ResponseABC):
    def __init__(self, status: Union[str, int], text: str):
        super().__init__(status, 'text/html')
        self.text = text

    def format_response(self):
        return [self.text.encode()]
