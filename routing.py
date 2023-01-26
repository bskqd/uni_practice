from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class Route:
    methods: list[str, ...]
    handler: Callable


class Router:
    def __init__(self):
        self._routes = {}

    def get_route(self, path: str) -> Optional[Route]:
        route: Optional[Route] = self._routes.get(path)
        if route:
            return route

    def route(self, path: str, methods: list[str]):
        def _route(request_handler: Callable):
            self._routes[path] = Route(methods=methods, handler=request_handler)
            return request_handler

        return _route
