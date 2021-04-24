import logging

from typing import List



from omdbweather.cache_engine import MovieCacheEngine
from omdbweather.handlers.base import BaseHandler, expect_json_data
from omdbweather.handlers.movie_client_helper import HttpClientMovieHelper

LOGGER = logging.getLogger(__name__)

class MoviesHandler(BaseHandler):
    def initialize(self, caches) -> None:
        self.caches = caches
        self._movie_helper = HttpClientMovieHelper()
    
    async def get(self):
        """
        ---
        tags:
        - Movies
        summary: get movies by query
        description: return full list of movies by query
        produces:
        - application/json
        parameters:
        -   name: f
            in: query
            description: fuzzy search
            required: false
            type: int
        -   name: q
            in: query
            description: query title
            required: false
            type: int
        -   name: str
            in: query
            description: string to search
            required: true
            type: string
        responses:
            200:
              description: list of posts
              schema:
                $ref: '#/definitions/Movie'
        """
        fuzzy = self.get_argument("f", default=None)
        if fuzzy and str(fuzzy) == "1":
            str_to_search = self.get_argument("str", default=None)
            if str_to_search is None:
                return self.write_ok([])
            results = await self._run_fuzzy_search(str_to_search)
            return self.write_ok([str(s) for s in results])

        query = self.get_argument("q", default=None)
        if query and str(query) == "1":
            str_to_search = self.get_argument("str", default=None)
            if str_to_search is None:
                return self.write_ok({})
            results = await self._run_search(str_to_search)
            if results is None:
                return self.handle_response_error(404, "movie not found")
            return self.write_ok(results)

        return self.handle_response_error(404, "No text found")

    async def _run_fuzzy_search(self, str_to_search: str) -> List:
        """
        return list of suggestion upon query string
        """
        self._movie_cache: MovieCacheEngine = self.caches["movie"]
        return self._movie_cache.get_suggestion(str_to_suggest=str_to_search)

    async def _run_search(self, str_to_search: str) -> List:
        """
        return list of movies from query string
        """
        self._movie_cache: MovieCacheEngine = self.caches["movie"]
        data = self._movie_cache.search(str_to_search)
        if data.total > 0:
            return [d.__dict__ for d in data.docs]
        movie_data = await self._movie_helper.search_movie_by_name(str_to_search)
        if movie_data is not None:
            return movie_data
        return None


class MovieHandler(BaseHandler):
    def initialize(self, caches) -> None:
        self.caches = caches
        self._movie_helper = HttpClientMovieHelper()
        self._movie_cache: MovieCacheEngine = self.caches["movie"]
    
    async def get(self, movie_id):
        """
        ---
        tags:
        - Movies
        summary: get movie by query
        description: return movie by query
        produces:
        - application/json
        parameters:
        -   name: movie_id
            in: path
            description: movie ID
            required: false
            type: string
        
        responses:
            200:
              description: list of posts
              schema:
                $ref: '#/definitions/Movie'
        """
        data = self._movie_cache.get_movie_by_id(movie_id)
        if data.total > 0:
            return self.write_ok([d.__dict__ for d in data.docs])
        data = await self._movie_helper.get_movie_by_id(movie_id=movie_id)
        if data is None:
            return self.handle_response_error(404, "Movie id not found")
        
        self._movie_cache.add_movie(data)
        return self.write_ok(data)



if __name__ == "__main__":
    pass

