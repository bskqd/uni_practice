from typing import Callable

from application import RequestABC, SimpleResponse


def authentication_required(request_handler: Callable):
    def _authentication_required(request: RequestABC):
        if not request.session or not request.session.get('username'):
            response = (
                '<!DOCTYPE html>'
                '<html lang="en">'
                '<head>'
                '<meta charset="UTF-8">'
                '<title>Тестування</title>'
                '</head>'
                '<body>'
                '<a href="http://uni_site.com/login_form.html">Спочатку авторизуйтесь</a>'
                '</body>'
                '</html>'
            )
            return SimpleResponse(401, response)
        return request_handler(request)

    return _authentication_required
