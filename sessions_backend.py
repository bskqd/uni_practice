import json
from typing import Optional

import redis

from wsgi_application.sessions import SessionsBackendABC


class RedisSessionsBackend(SessionsBackendABC):
    def __init__(self, host: str, port: int, db: int, password: Optional[str] = None):
        self.redis = redis.Redis(host=host, port=port, db=db, password=password)

    def get_session_data(self, session_id: str) -> dict:
        if not session_id:
            return {}
        existing_session_data = self.redis.get(session_id)
        if existing_session_data:
            return json.loads(existing_session_data)
        return {}

    def write_session_data(self, session_id: str, data: dict):
        if not session_id:
            return
        self.redis.set(session_id, json.dumps(data))
