from endpoints import router
from wsgi_application.application import Application


def create_application() -> Application:
    app = Application()

    app.include_router(router)

    app.set_authentication_failed_redirect_path('http://uni_site.com/login_form.html')

    return app


application = create_application()
