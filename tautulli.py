import re

import pendulum
import requests


class Tautulli:
    config_passed = False
    movie_count = None
    movie_list = []

    def __init__(self, config: dict, BASE_URL, get_movies=False):
        self.port = config.get('port', None)
        self.api_key = config.get('api_key', None)
        self.api_route = config.get('api_route', None)
        self.base_url = BASE_URL
        self.check_status()
        self.get_movies() if get_movies else None

    def check_status(self):
        # print(f'port: {self.port} API Key: "{self.api_key}", Route: "{self.api_route}"')

        payload = {"apikey": self.api_key, "cmd": "server_status"}
        status = requests.request("get", f"{self.base_url}:{self.port}{self.api_route}", params=payload)
        if status.status_code == 200:
            print(status.json())
            self.config_passed = True

        else:
            self.config_passed = False

    def get_movies(self):
        if self.config_passed:
            payload = {
                "apikey": self.api_key, "cmd": "get_library_media_info", "section_id": 1,
                "refresh": True, "length": 10000}

            request = requests.request("get", f"{self.base_url}:{self.port}{self.api_route}", params=payload)

            request_json = request.json()
            self.movie_count = request_json['response']['data']['recordsFiltered']
            data = request_json['response']['data']['data']
            [self.movie_list.append(movie) for movie in data]
            return self.movie_list

    def get_movie_details(self, rating_key):
        if self.config_passed:
            payload = {
                "apikey": self.api_key, "cmd": "get_metadata", "rating_key": rating_key}

            request = requests.request("get", f"{self.base_url}:{self.port}{self.api_route}", params=payload)
            request_json = request.json()
            movie_data = request_json['response']['data']
            return movie_data

    def get_ignored_movies(self, threshold_in_days: int = 30):
        if not self.movie_list:
            self.get_movies()
        filtered_movies = []
        count = 0
        date_today = pendulum.DateTime.now()
        threshold_date = date_today.subtract(days=threshold_in_days)
        for movie in self.movie_list:
            if pendulum.from_timestamp(int(movie['added_at'])) <= threshold_date and movie['play_count'] is None:
                filtered_movies.append(movie)
                count += 1
        return filtered_movies

    def get_imdb_guid(self, rating_key):
        movie = self.get_movie_details(rating_key)
        guid_string = movie.get('guid', None)
        if guid_string:
            guid = re.split('//|\?', guid_string)
            return guid[1]
