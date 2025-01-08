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
        page,
        items_per_page,
        adult,
    ):
        res = self._backend.search(q, page, items_per_page, adult)
        results_dict_format = []
        for r in res:
            record = {
                "url_id": r[0],  # p.url_id
                "url": r[1],  # u.url
                "title": r[2],  # p.title
                "description": r[3],  # p.description
                "icon": r[4],  # p.icon
                "score": r[5],  # Calculated score (0.7 * pdb_score + 0.3 * pr_score)
                "pdb_score": r[6],  # paradedb.score(p.url_id)
                "pr_score": r[7]  # pr.rank
            }
            results_dict_format.append(record)
        self._add_to_history(q)
        return res

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
