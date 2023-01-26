from application import Application
from endpoints import router


def create_application() -> Application:
    app = Application()

    app.include_router(router)

    return app


application = create_application()
