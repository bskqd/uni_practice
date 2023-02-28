from database.base import session_maker
from wsgi_application.database import DatabaseSessionMakerABC


class DatabaseSessionMaker(DatabaseSessionMakerABC):
    def open_session(self):
        self.__session = session_maker()
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def close(self):
        self.__session.close()
