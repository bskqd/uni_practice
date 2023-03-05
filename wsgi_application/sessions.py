import abc
import json
import os
import uuid


class SessionsBackendABC(abc.ABC):
    def generate_session_id(self) -> str:
        return uuid.uuid4().hex

    @abc.abstractmethod
    def get_session_data(self, session_id: str) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    def write_session_data(self, session_id: str, data: dict):
        raise NotImplementedError


class FilesystemSessionsBackend(SessionsBackendABC):
    def get_session_data(self, session_id: str) -> dict:
        if not session_id:
            return {}
        os.makedirs('sessions', exist_ok=True)
        session_file_path = os.path.join('sessions', f'{session_id}.json')
        if not os.path.exists(session_file_path):
            with open(session_file_path, 'w') as f:
                f.write('{}')
            return {}
        with open(session_file_path, 'r') as f:
            session_data = json.load(f)
        return session_data

    def write_session_data(self, session_id: str, data: dict):
        if not session_id:
            return
        os.makedirs('sessions', exist_ok=True)
        session_file_path = os.path.join('sessions', f'{session_id}.json')
        with open(session_file_path, 'w') as f:
            json.dump(data, f)
