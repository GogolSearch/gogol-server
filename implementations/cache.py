import redis

class RedisCache:
    def __init__(self, redis_client : redis.Redis, queries_list_key):
        self._redis_client = redis_client
        self._queries_list_key = queries_list_key

    def add_query(self, *queries):
        return self._redis_client.lpush(self._queries_list_key,*queries)

    def get_all_queries(self):
        return self._redis_client.lrange(self._queries_list_key, 0, -1)