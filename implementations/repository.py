from implementations.backend import PostgreSQLBackend
from implementations.cache import  RedisCache


class QueryRepository:
    """Répertoire des données de crawl qui encapsule toutes les interactions avec les données"""

    def __init__(
    self,
            cache: RedisCache,
            backend: PostgreSQLBackend,
    ):
        """
        Initializes the query repository with a cache and a backend manager.
        """
        self._cache = cache
        self._backend = backend

    def _add_to_history(self, query: str):
        self._cache.add_query(query)

    def search(
        self,
        q: str,
        page,
        items_per_page,
        adult,
    ):
        res = self._backend.search(q, page, items_per_page, adult)
        self._add_to_history(q)

        return res

    def get_history(self, q:str, n: int):
        matching = []
        results = self._cache.get_all_queries()
        for r in results:
            if q in r:
                if len(results) <= n:
                    matching.append(r)
                else:
                    break
        return matching
