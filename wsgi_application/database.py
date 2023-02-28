import abc


class DatabaseSessionMakerABC:
    def __enter__(self):
        return self.open_session()

    def __exit__(self, *args):
        self.rollback()
        self.close()

    @abc.abstractmethod
    def open_session(self):
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

    @abc.abstractmethod
    def close(self):
        raise NotImplementedError


class FakeDatabaseSessionMaker(DatabaseSessionMakerABC):
    def open_session(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass
