import logging
from typing import List

from redisearch import Client, TextField, IndexDefinition, Query, TagField, Result, AutoCompleter, Suggestion
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
    
    def add_doc(self, doc_id: str, data: dict) -> bool:
        if dict is None:
            return False
        results = self._client.add_document(doc_id, replace=True, **data)
        return results

    def search(self, text_to_search: str) -> Result:
        results: Result = self._client.search(text_to_search)
        q = Query("search engine").verbatim().no_content().paging(0,5)
        return results
    
    def add_suggestion(self, suggestion) -> bool:
        results = None
        try:
            returls = self._auto_compl.add_suggestions(Suggestion(suggestion))
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
        info_exists = self._client.info()
        if info_exists:
            self._client.drop_index()
        self._client.create_index([
            TextField('title', weight=5.0),
            TextField('Year'),
            TextField('Released'),
            TextField('Runtime'),
            TextField('Director'),
            TagField('Genre'),
            TextField('Writer'),
            TagField('Actors'),
            TextField('Plot'),
            TagField('Language'),
            TextField('Country'),
            TextField('Awards'),
            TextField('Poster'),
            TextField('Ratings'),
            TextField('Metascore'),
            NumericField('imdbRating'),
            NumericField('imdbVotes'),
            NumericField('imdbID'),
            TextField('Type'),
            NumericField('totalSeasons'),
            TextField('Response'),
        ])
    
    def add_movie(self, movie_data: dict) -> bool:
        if "imdbID" not in movie_data or "Title" not in movie_data:
            LOGGER.warning("movie id or title doenst exists")
            return False
        movie_add_results = self.add_doc(movie_data["imdbID"], movie_data)
        movie_add_sugg = self.add_suggestion(movie_data["Title"])
        return movie_add_results is True and movie_add_sugg is True




if __name__ == "__main__":
    d = dict(
        {
            "Title": "Mr. asdaot",
            "Year": "2015–2019",
            "Rated": "TV-MA",
            "Released": "24 Jun 2015",
            "Runtime": "49 min",
            "Genre": "Crime, Drama, Thriller",
            "Director": "N/A",
            "Writer": "Sam Esmail",
            "Actors": "Rami Malek, Christian Slater, Carly Chaikin, Martin Wallström",
            "Plot": "Elliot, a brilliant but highly unstable young cyber-security engineer and vigilante hacker, becomes a key figure in a complex game of global dominance when he and his shadowy allies try to take down the corrupt corporation he works for.",
            "Language": "English, Swedish, Danish, Chinese, Persian, Spanish, Arabic, German",
            "Country": "USA",
            "Awards": "Won 2 Golden Globes. Another 19 wins & 79 nominations.",
            "Poster": "https://m.media-amazon.com/images/M/MV5BMzgxMmQxZjQtNDdmMC00MjRlLTk1MDEtZDcwNTdmOTg0YzA2XkEyXkFqcGdeQXVyMzQ2MDI5NjU@._V1_SX300.jpg",
            
            "Metascore": "N/A",
            "imdbRating": "8.5",
            "imdbVotes": "336,545",
            "imdbID": "ta41qw58110",
            "Type": "series",
            "totalSeasons": "4",
            "Response": "True"
        }
    )
    d2 = dict(
        {
            "Title": "Mr. Rffdsd",
            "Year": "2015–2019",
            "Rated": "TV-MA",
            "Released": "24 Jun 2015",
            "Runtime": "49 min",
            "Genre": "Crime, Drama, Thriller",
            "Director": "N/A",
            "Writer": "Sam Esmail",
            "Actors": "Rami Malek, Christian Slater, Carly Chaikin, Martin Wallström",
            "Plot": "Elliot, a brilliant but highly unstable young cyber-security engineer and vigilante hacker, becomes a key figure in a complex game of global dominance when he and his shadowy allies try to take down the corrupt corporation he works for.",
            "Language": "English, Swedish, Danish, Chinese, Persian, Spanish, Arabic, German",
            "Country": "USA",
            "Awards": "Won 2 Golden Globes. Another 19 wins & 79 nominations.",
            "Poster": "https://m.media-amazon.com/images/M/MV5BMzgxMmQxZjQtNDdmMC00MjRlLTk1MDEtZDcwNTdmOTg0YzA2XkEyXkFqcGdeQXVyMzQ2MDI5NjU@._V1_SX300.jpg",
            
            "Metascore": "N/A",
            "imdbRating": "8.5",
            "imdbVotes": "336,545",
            "imdbID": "ta4r158110",
            "Type": "series",
            "totalSeasons": "4",
            "Response": "True"
        }
    )
    c = MovieCacheEngine("localhost")    
    c.add_movie(d)
    c.add_movie(d2)

    c.get_suggestion("Mr.")
