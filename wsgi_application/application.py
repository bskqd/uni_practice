from typing import Callable

from wsgi_application.authentication import AuthenticationError
from wsgi_application.request import RequestCreator, Request
from wsgi_application.response import ResponseABC, SimpleResponse
from wsgi_application.routing import Router, Route


class Application:
    def __init__(self):
        self._routers: list[Router, ...] = []
        self._authentication_failed_redirect_path = ''
        self.__request_creator = RequestCreator()

    def __call__(self, environ: dict, start_response: Callable):
        request = self.__request_creator.create_request(environ)
        try:
            response: ResponseABC = self.handle_request(request)
        except AuthenticationError:
            start_response('302', [('Location', self._authentication_failed_redirect_path)])
            return []
        start_response(str(response.status), response.headers)
        return response.format_response()

    def include_router(self, router: Router):
        self._routers.append(router)

    def set_authentication_failed_redirect_path(self, path: str):
        self._authentication_failed_redirect_path = path

    def handle_request(self, request: Request) -> ResponseABC:
        for router in self._routers:
            route: Route = router.get_route(path=request.path)
            if route:
                if request.method not in route.methods:
                    return SimpleResponse(405, 'Method is not allowed')
                return route.handler(request)
        return SimpleResponse(404, 'Path is not valid')
