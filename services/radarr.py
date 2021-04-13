"""A Radarr API wrapper to work with PyTulli"""
import json

import requests


class Radarr:
    """The Radarr class uses Radarr's existing API to make requests."""
    config_passed = False

    def __init__(self, config: dict, BASE_URL):
        self.port = config.get('port', None)
        self.api_key = config.get('api_key', None)
        self.api_route = config.get('api_route', None)
        self.base_url = BASE_URL

        self.check_status()

    def check_status(self) -> bool:
        """A method to verify config is set correctly and that Radarr is handling requests."""
        # print(f'port: {self.port} API Key: "{self.api_key}", Route: "{self.api_route}"')

        payload = {"apikey": self.api_key}
        status = requests.request("get", f"{self.base_url}:{self.port}{self.api_route}/system/status", params=payload)
        # print(status.json())
        if status.status_code == 200:
            self.config_passed = True
        else:
            self.config_passed = False
        return self.config_passed

    def get_movies(self) -> dict:
        """This method requests a list of all movies in Radarr's database."""
        url = f"{self.base_url}:{self.port}{self.api_route}/movie?length=10000"

        payload = {}
        headers = {
            'X-Api-Key': self.api_key
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        return response.json()

    def delete_movie(self, _id) -> dict:
        """Makes a DELETE request to Radarr. Radarr will delete the movie and associated files on PMS."""
        url = f"{self.base_url}:{self.port}{self.api_route}/movie/{_id}?deleteFiles=true"

        payload = {}
        headers = {
            'X-Api-Key': self.api_key
        }

        response = requests.request("DELETE", url, headers=headers, data=payload)
        with open('../deleted.log', 'a+') as file:
            file.write(json.dumps(response.json()))
        # print(response.json())
        return response.json()
