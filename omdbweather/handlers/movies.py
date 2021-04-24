from typing import List

from omdbweather.cache_engine import MovieCacheEngine
from omdbweather.handlers.base import BaseHandler, expect_json_data


class MoviesHandler(BaseHandler):
    def initialize(self, caches) -> None:
        self.caches = caches
    
    async def get(self):
        fuzzy = self.get_argument("f", default=None)
        if fuzzy and str(fuzzy) == "1":
            str_to_search = self.get_argument("str", default=None)
            if str_to_search is None:
                return self.write_ok([])
            results = await self._run_fuzzy_search(str_to_search)
            return self.write_ok([str(s) for s in results])

        query = self.get_argument("q", default=None)
        if query and str(query) == "1":
            str_to_search = await self.get_argument("str", default=None)
            if str_to_search is None:
                return self.write_ok({})
            results = self._run_search(str_to_search)
            return self.write_ok(results)

        return self.handle_response_error(404, "No text found")

    async def _run_fuzzy_search(self, str_to_search: str) -> List:
        self._movie_cache: MovieCacheEngine = self.caches["movie"]
        return self._movie_cache.get_suggestion(str_to_suggest=str_to_search)

    async def _run_search(self, str_to_search: str) -> List:
        pass

    @expect_json_data
    async def post(self, container_name, data):
        pass

if __name__ == "__main__":
    pass
