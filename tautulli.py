from movie import Movie

from pytulli import config
import requests


class Tautulli:
    """The class to work with the Tautulli API"""

    def __init__(self):
        self.movies = []
        self.API_KEY = config.get("TAUTULLI.API_KEY")
        self.API_ENDPOINT = config.get("TAUTULLI.API_ENDPOINT")
        self.SECTION_ID = config.get("TAUTULLI.SECTION_ID")
        self.movie_count = self._get_library_count()

    def _refresh_libraries_list(self):
        """Sends a command to refresh Tautulli's movie database"""
        payload = {"apikey": self.API_KEY, "cmd": "refresh_libraries_list"}
        requests.get(self.API_ENDPOINT, params=payload)
        self.movie_count = self._get_library_count()
        return None

    def _get_library_count(self):
        """Gets total count of movies in library"""
        payload = {"apikey": self.API_KEY, "cmd": "get_library", "section_id": self.SECTION_ID}
        r = requests.get(self.API_ENDPOINT, params=payload)
        data = r.json()
        return data["response"]["data"]['count']

    def get_movie_library(self):
        """Returns list of movies in Movie Object form from the library."""
        self._refresh_libraries_list()
        payload = {"apikey": self.API_KEY, "cmd": "get_library_media_info", "section_id": self.SECTION_ID,
                   "length": self.movie_count, "refresh": True}
        r = requests.get(self.API_ENDPOINT, params=payload)
        data = r.json()
        for movie in data["response"]["data"]["data"]:
            self.movies.append(
                Movie(movie['title'],
                      movie['sort_title'],
                      movie['rating_key'],
                      movie['year'],
                      movie['added_at'],
                      movie['last_played'],
                      movie['play_count']))
        return self.movies

    def get_metadata(self, rating_key):
        """Returns dictionary of movie details"""
        payload = {"apikey": self.API_KEY, "cmd": "get_metadata", "rating_key": rating_key}
        r = requests.get(self.API_ENDPOINT, params=payload)
        data = r.json()
        return data


if __name__ == "__main__":
    tautulli = Tautulli()
    library = tautulli.get_movie_library()
    [print(f"{movie.title}, {movie.rating_key}") for movie in sorted(library, key=lambda x: x.sort_title)]
    print(len(library))
