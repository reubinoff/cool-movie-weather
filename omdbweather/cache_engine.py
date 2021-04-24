import logging
import json
from typing import Any, List

from redisearch import Client, TextField, IndexDefinition, Query, TagField, Result, AutoCompleter, Suggestion, Document
from redisearch import result
from redisearch.client import NumericField
from redisearch.result import Result


LOGGER = logging.getLogger(__name__)


class CacheEngine:
    def __init__(self, hostname: str, idx_name: str, port=6379) -> None:
        self._ready = False
        self._setup_client(hostname, idx_name, port)

    def _setup_client(self, hostname: str, idx_name: str, port=6379) -> None:
        try:
            self._client = Client(idx_name, host=hostname, port=port)
            self._auto_compl = AutoCompleter(idx_name, hostname, port=port)
            self._hostname = hostname
            self._port = port
            self._idx = idx_name
            self._ready = True
            LOGGER.info("Cache engine is ready")
        except:
            self._client = None
            LOGGER.error("Cache engine is faulty!")
    
    def add_doc(self, doc_id: str, data: dict) -> Any:
        if dict is None:
            return False
        results = self._client.redis.hset(doc_id, mapping=data)
        return results

    def search(self,text_to_search: str) -> Result:
        results: Result = self._client.search(text_to_search)
        return results
    
    def get_doc(self, doc_id) -> Document:
        try:
            data = self._client.load_document(doc_id)
            return data
        except:
            return None
    
    def add_suggestion(self, suggestion) -> bool:
        results = None
        try:
            results = self._auto_compl.add_suggestions(Suggestion(suggestion))
        except:
            return False
        return True

    def get_suggestion(self, str_to_suggest: str) -> List:
        suggs = self._auto_compl.get_suggestions(str_to_suggest, fuzzy = len(str_to_suggest) > 3)
        return suggs
        



class MovieCacheEngine(CacheEngine):
    def __init__(self, hostname: str) -> None:
        self._idx_name = "movies"
        super().__init__(hostname, self._idx_name)
        try:
            info_exists = self._client.info()
            if info_exists:
                self._client.drop_index()
        except:
            pass
        definition = IndexDefinition(prefix=[f'{self._idx_name}:'])

        self._client.create_index((
            TextField('Title'),
            TextField('Plot'),
            TextField('imdbID'),
        ), definition=definition)
    
    def add_movie(self, movie_data: dict) -> bool:
      

        if "imdbID" not in movie_data or "Title" not in movie_data:
            LOGGER.warning("movie id or title doenst exists")
            return False
        movie_data["Ratings"] = json.dumps(movie_data["Ratings"])
        movie_id = f"{self._idx_name}:" + movie_data["imdbID"]
        movie_add_results = self.add_doc(movie_id, movie_data)
        movie_add_sugg = self.add_suggestion(movie_data["Title"])
        return  movie_add_results == "OK" and movie_add_sugg is True
    
    def get_movie_by_id(self, movie_id) -> Document:
        try:
            data = self._client.search(movie_id)
            return data
        except:
            return None



if __name__ == "__main__":
    pass