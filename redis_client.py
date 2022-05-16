import os
import redis


class RedisClient:
    def __init__(self):
        self.pool = redis.ConnectionPool(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            db=1,
        )

    def set_connection(self) -> None:
        self._conn = redis.Redis(connection_pool=self.pool)

    @property
    def connection(self):
        if not hasattr(self, "_conn"):
            self.set_connection()
        return self._conn
