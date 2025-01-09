import html

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
        self._cache.remove_query(query)
        self._cache.add_query(query)

    def search(
        self,
        q: str,
        start,
        items_per_page,
    ):
        res = self._backend.search(q, start, items_per_page)
        results_dict_format = []
        for r in res:
            if r[5] is None:
                print(r)
            record = {
                "url_id": int(r[0]),  # p.url_id
                "url": str(r[1]),  # u.url
                "title": str(r[2]),  # p.title
                "description": str(r[3]),  # p.description
                "icon": str(r[4]),  # p.icon
                "score": float(r[5]),  # Calculated score (0.7 * pdb_score + 0.3 * pr_score)
                "pdb_score": float(r[6]),  # paradedb.score(p.url_id)
                "pr_score": float(r[7]),  # pr.rank
                "total_results": int(r[8]),
            }
            results_dict_format.append(record)
        self._add_to_history(q)
        return results_dict_format

    def get_history(self, q:str, n: int):
        matching = []
        results = self._cache.get_all_queries()
        for r in results:
            if q.lower() in r.lower():
                if len(matching) <= n:
                    matching.append(r)
                else:
                    break
        return matching
