from gunicorn.app.wsgiapp import WSGIApplication

from database.wsgi_sessionmaker import DatabaseSessionMaker
from endpoints import router
from sessions_backend import RedisSessionsBackend
from wsgi_application.application import Application


def create_application() -> Application:
    app = Application()

    app.include_router(router)

    app.set_authentication_failed_redirect_path('http://uni_site.com/login_form.html')

    app.set_database_session_maker(DatabaseSessionMaker)

    app.set_sessions_backend(RedisSessionsBackend(host='localhost', port=6379, db=0))

    app.set_templates_path('static/templates')

    return app


application = create_application()


class StandaloneApplication(WSGIApplication):
    def __init__(self, app_uri, options=None):
        self.options = options or {}
        self.app_uri = app_uri
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)


if __name__ == '__main__':
    StandaloneApplication('main:application', {'config': 'gunicorn.conf.py'}).run()
