import abc
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Callable, Union
from urllib import parse

from routing import Router, Route


class Request(abc.ABC):
    def __init__(self, path: str, method: str, cookies_string: str):
        self.path: str = path
        self.method: str = method
        self.cookies: dict = self.parse_cookies(cookies_string)
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
        for cookie in cookies_string.split(';'):
            cookie = cookie.split('=')
            cookies[cookie[0]] = parse.unquote(cookie[1])
        return cookies


class PostRequest(Request):
    def __init__(self, path: str, cookies_string: str):
        super().__init__(path, 'POST', cookies_string)


class GetRequest(Request):
    def __init__(self, path: str, cookies_string: str):
        super().__init__(path, 'GET', cookies_string)


class RequestCreator(abc.ABC):
    @abc.abstractmethod
    def create_request(self, environ: dict) -> Request:
        pass


class PostRequestCreator(RequestCreator):
    def create_request(self, environ: dict) -> Request:
        post_request = PostRequest(path=environ['PATH_INFO'], cookies_string=environ.get('HTTP_COOKIE', ''))
        post_request.fill_params(parse.parse_qs(environ['wsgi.input'].read().decode(), keep_blank_values=True))
        return post_request


class GetRequestCreator(RequestCreator):
    def create_request(self, environ: dict) -> Request:
        get_request = GetRequest(path=environ['PATH_INFO'], cookies_string=environ.get('HTTP_COOKIE', ''))
        get_request.fill_params(parse.parse_qs(environ['QUERY_STRING']))
        return get_request


class RequestCreatorFactoryABC(abc.ABC):
    @abc.abstractmethod
    def create_request(self, environ: dict) -> Request:
        pass


class RequestCreatorFactory(RequestCreatorFactoryABC):
    def __init__(self):
        self._requests_creators: dict[str, RequestCreator] = {
            'POST': PostRequestCreator(),
            'GET': GetRequestCreator(),
        }

    def create_request(self, environ: dict) -> Request:
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

    def set_cookie_header(self, key: str, value: str, seconds: int = 60 * 10):
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

    def handle_request(self, request: Request) -> ResponseABC:
        for router in self._routers:
            route: Route = router.get_route(path=request.path)
            if route:
                if request.method not in route.methods:
                    return SimpleResponse(405, 'Method is not allowed')
                return route.handler(request)
        return SimpleResponse(404, 'Path is not valid')
