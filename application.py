import abc
import json
import uuid
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Callable, Union
from urllib import parse

from cryptography.fernet import Fernet

from routing import Router, Route

fernet = Fernet(b'ZZqGR87-stO2XPezRzJwKM7L5MLSdnc3KlxmXew5G5I=')


class RequestABC(abc.ABC):
    def __init__(self, path: str, method: str, cookies_string: str):
        self.path: str = path
        self.method: str = method
        self.cookies: dict = self.parse_cookies(cookies_string)
        self.session: dict = self.load_session()
        self.params: dict = {}

    def fill_params(self, parsed_params: dict[str, list[str]]):
        for k, v in parsed_params.items():
            if isinstance(v, list) and len(v) == 1:
                self.params[k] = v[0]
                continue
            self.params[k] = v

    def parse_cookies(self, cookies_string: str) -> dict:
        cookies = {}
        if not cookies_string:
            return cookies
        for cookie in cookies_string.split('; '):
            cookie = cookie.split('=')
            cookies[cookie[0]] = parse.unquote(cookie[1])
        return cookies

    # TODO: figure out what's wrong with fernet encrypted data in sessions
    # def load_session(self) -> dict:
    #     try:
    #         return json.loads(fernet.decrypt(self.cookies['session'].encode()).decode())
    #     except (json.JSONDecodeError, KeyError, InvalidToken):
    #         return {}

    # def load_session(self) -> dict:
    #     try:
    #         return json.loads(self.cookies['session'])
    #     except (json.JSONDecodeError, KeyError, InvalidToken):
    #         return {}

    def load_session(self) -> dict:
        session_id = self.cookies['session']
        with open('sessions.json', 'r') as f:
            sessions_data = json.load(f)
        session_data = sessions_data.get(session_id)
        if not session_data:
            return {}
        return json.loads(fernet.decrypt(session_data.encode()).decode())


class PostRequest(RequestABC):
    def __init__(self, path: str, cookies_string: str):
        super().__init__(path, 'POST', cookies_string)


class GetRequest(RequestABC):
    def __init__(self, path: str, cookies_string: str):
        super().__init__(path, 'GET', cookies_string)


class RequestCreatorABC(abc.ABC):
    @abc.abstractmethod
    def create_request(self, environ: dict) -> RequestABC:
        pass


class PostRequestCreator(RequestCreatorABC):
    def create_request(self, environ: dict) -> RequestABC:
        post_request = PostRequest(path=environ['PATH_INFO'], cookies_string=environ.get('HTTP_COOKIE', ''))
        post_request.fill_params(parse.parse_qs(environ['wsgi.input'].read().decode(), keep_blank_values=True))
        return post_request


class GetRequestCreator(RequestCreatorABC):
    def create_request(self, environ: dict) -> RequestABC:
        get_request = GetRequest(path=environ['PATH_INFO'], cookies_string=environ.get('HTTP_COOKIE', ''))
        get_request.fill_params(parse.parse_qs(environ['QUERY_STRING']))
        return get_request


class RequestCreatorFactoryABC(abc.ABC):
    @abc.abstractmethod
    def create_request(self, environ: dict) -> RequestABC:
        pass


class RequestCreatorFactory(RequestCreatorFactoryABC):
    def __init__(self):
        self._requests_creators: dict[str, RequestCreatorABC] = {
            'POST': PostRequestCreator(),
            'GET': GetRequestCreator(),
        }

    def create_request(self, environ: dict) -> RequestABC:
        request_creator = self._requests_creators.get(environ['REQUEST_METHOD'])
        return request_creator.create_request(environ)


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

    # TODO: figure out what's wrong with fernet encrypted data in sessions
    # def set_session(self, session_data: dict):
    #     self.__set_cookie_header('session', fernet.encrypt(json.dumps(session_data).encode()).decode())

    # def set_session(self, session_data: dict):
    #     self.__set_cookie_header('session', json.dumps(session_data).encode().decode())

    def set_session(self, session_data: dict):
        session_id = uuid.uuid4().hex
        self.__set_cookie_header('session', session_id)
        with open('sessions.json', 'r') as f:
            sessions_data = json.load(f)
        sessions_data[session_id] = fernet.encrypt(json.dumps(session_data).encode()).decode()
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


class Application:
    def __init__(self):
        self._routers: list[Router, ...] = []
        self.__request_creator_factory = RequestCreatorFactory()

    def __call__(self, environ: dict, start_response: Callable):
        request = self.__request_creator_factory.create_request(environ)
        response: ResponseABC = self.handle_request(request)
        start_response(str(response.status), response.headers)
        return response.format_response()

    def include_router(self, router: Router):
        self._routers.append(router)

    def handle_request(self, request: RequestABC) -> ResponseABC:
        for router in self._routers:
            route: Route = router.get_route(path=request.path)
            if route:
                if request.method not in route.methods:
                    return SimpleResponse(405, 'Method is not allowed')
                return route.handler(request)
        return SimpleResponse(404, 'Path is not valid')
