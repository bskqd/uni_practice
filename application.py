import abc
from typing import Callable
from urllib import parse

from routing import Router, Route


class Request(abc.ABC):
    def __init__(self, path: str, method: str, cookies_string: str):
        self.path: str = path
        self.method: str = method
        self.cookies: dict = self.parse_cookies(cookies_string)
        self.body: dict = {}
        self.query_params: dict = {}

    @abc.abstractmethod
    def fill_request_data(self):
        pass

    def parse_cookies(self, cookies_string: str) -> dict:
        cookies = {}
        if not cookies_string:
            return cookies
        for cookie in cookies_string.split(';'):
            cookie = cookie.split('=')
            cookies[cookie[0]] = parse.unquote(cookie[1])
        return cookies


class PostRequest(Request):
    def __init__(self, path: str, method: str, cookies_string: str, body_initial_string: str):
        super().__init__(path, method, cookies_string)
        self.body_initial_string = body_initial_string

    def fill_request_data(self):
        parsed_body = parse.parse_qs(self.body_initial_string, keep_blank_values=True)
        for k, v in parsed_body.items():
            if isinstance(v, list) and len(v) == 1:
                self.body[k] = v[0]
                continue
            self.body[k] = v


class GetRequest(Request):
    def __init__(self, path: str, method: str, cookies_string: str, query_params_string: str):
        super().__init__(path, method, cookies_string)
        self.query_params_string = query_params_string

    def fill_request_data(self):
        parsed_query_params = parse.parse_qs(self.query_params_string)
        for k, v in parsed_query_params.items():
            if isinstance(v, list) and len(v) == 1:
                self.query_params[k] = v[0]
                continue
            self.query_params[k] = v


class RequestCreator(abc.ABC):
    @abc.abstractmethod
    def create_request(self, environ: dict) -> Request:
        pass


class PostRequestCreator(RequestCreator):
    def create_request(self, environ: dict) -> Request:
        post_request = PostRequest(
            path=environ['PATH_INFO'],
            method='POST',
            cookies_string=environ.get('HTTP_COOKIE', ''),
            body_initial_string=environ['wsgi.input'].read().decode(),
        )
        post_request.fill_request_data()
        return post_request


class GetRequestCreator(RequestCreator):
    def create_request(self, environ: dict) -> Request:
        get_request = GetRequest(
            path=environ['PATH_INFO'],
            method='GET',
            cookies_string=environ.get('HTTP_COOKIE', ''),
            query_params_string=environ['QUERY_STRING'],
        )
        get_request.fill_request_data()
        return get_request


class Application:
    def __init__(self):
        self._routers: list[Router, ...] = []
        self._requests_creators: dict[str, RequestCreator] = {
            'POST': PostRequestCreator(),
            'GET': GetRequestCreator(),
        }

    def __call__(self, environ: dict, start_response: Callable):
        request_creator = self._requests_creators.get(environ['REQUEST_METHOD'])
        request = request_creator.create_request(environ)
        return self.handle_request(request, start_response)

    def include_router(self, router: Router):
        self._routers.append(router)

    def handle_request(self, request: Request, start_response: Callable):
        for router in self._routers:
            route: Route = router.get_route(path=request.path)
            if route:
                if request.method not in route.methods:
                    start_response('405 MethodNotAllowed', [('Content-Type', 'text/html')])
                    return ['Method is not allowed'.encode()]
                return route.handler(request, start_response)
        start_response('404 NotFound', [('Content-Type', 'text/html')])
        return ['Path is not valid'.encode()]
