from typing import Callable

from routing import Router, Route


class Application:
    def __init__(self):
        self._routers: list[Router, ...] = []

    def __call__(self, environ: dict, start_response: Callable):
        return self.handle_request(environ, start_response)

    def include_router(self, router: Router):
        self._routers.append(router)

    def handle_request(self, environ: dict, start_response: Callable):
        for router in self._routers:
            route: Route = router.get_route(path=environ['PATH_INFO'])
            if route:
                if environ['REQUEST_METHOD'] not in route.methods:
                    start_response('405 MethodNotAllowed', [('Content-Type', 'text/html')])
                    return ['Method is not allowed'.encode()]
                return route.handler(environ, start_response)
        start_response('404 NotFound', [('Content-Type', 'text/html')])
        return ['Path is not valid'.encode()]
