import logging
import json
from typing import List
from urllib.parse import quote
from tornado.httpclient import AsyncHTTPClient

LOGGER = logging.getLogger(__name__)


class HttpClientMovieHelper:
    def __init__(self) -> None:
        self._http_client = AsyncHTTPClient()

    async def get_movie_by_id(self, movie_id):
        data = await self.movie_search_api(movie_id, "i")
        if data is None or ("Response" in data and data["Response"] is False):
            return None
        if "imdbID" in data:
            title = data.get("Title")
            LOGGER.info(f"featch movie: {title}")
            return data
       
        return data

    async def get_movie_by_name(self, movie_name):
        data = await self.movie_search_api(movie_name, "t")
        if data is None or ("Response" in data and data["Response"] is False):
            return None
        if "imdbID" in data:
            title = data.get("Title")
            LOGGER.info(f"featch movie: {title}")
            return data
        return data

    async def search_movie_by_name(self, movie_name) -> List:
        data = await self.movie_search_api(movie_name, "s")
        if data is None or "Search" not in data:
            return None
        if "Search" in data and len(data["Search"]) > 0:
            return [movie for movie in data["Search"]]
        return None


    async def movie_search_api(self, query_str, query_letter="i"):
        response = None
        try:
            response = await self._http_client.fetch(f"http://www.omdbapi.com/?{query_letter}={quote(query_str)}&apikey=dce24c91")
        except Exception as e:
            LOGGER.error("Error: %s" % e)
            return None
        data = json.loads(response.body)
        
    
        return data