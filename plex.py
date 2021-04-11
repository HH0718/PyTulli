import json
import webbrowser
from time import sleep

import requests
from vyper import v

v.set_config_name("config")
v.add_config_path('.')
v.read_in_config()


class Plex:
    plex_client_id = "2a4290e1-6613-4b81-8811-13194c023f49"
    plex_token = None

    def __init__(self, config: dict, BASE_URL):
        self.config = config
        self.port = config.get('port', None)

        self.base_url = BASE_URL

    def get_pms_token(self):
        _id = None
        validated = False
        url = "https://plex.tv/api/v2/pins"
        payload = {"X-Plex-Product": "pytulli", "X-Plex-Client-Identifier": self.plex_client_id, "strong": True}
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response_json = response.json()
        print(response_json)
        _id = response_json.get('id')
        code = response_json.get('code')
        auth_url = f"https://app.plex.tv/auth/#?code={code}&clientID={self.plex_client_id}"
        webbrowser.open(auth_url, new=1)
        sleep(2)
        while not validated:
            url = f"https://plex.tv/api/v2/pins/{_id}"
            payload = {"code": code, "X-Plex-Client-Identifier": self.plex_client_id, "strong": True}
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.request("get", url, headers=headers, data=payload)
            response_json = response.json()
            # print(response_json)
            if response_json.get('authToken'):
                self.plex_token = response_json.get('authToken')
                with open('plex.token.json', 'w+') as file:
                    file.write(json.dumps({"token": self.plex_token}))
                validated = True
            else:
                print("sleeping")
                sleep(1)
        print(self.plex_token)

    def verify_pms_token(self):
        try:
            with open('plex.token.json', 'r+') as file:

                data = json.load(file)

                self.plex_token = data.get('token', None)
        except:
            pass
        if not self.plex_token:
            self.get_pms_token()

        url = "https://plex.tv/api/v2/user"
        payload = {
            "X-Plex-Product": "pytulli", "X-Plex-Client-Identifier": self.plex_client_id, "X-Plex-Token":
                self.plex_token}
        headers = {"Accept": "application/json"}

        response = requests.request("GET", url, headers=headers, data=payload)
        print(json.dumps(response.json(), indent=4))

    def logout_pms(self):
        with open('plex.token.json', "w+") as file:
            file.write('')
            print("logged out successfully")

    def refresh_movie_metadata(self, rating_key):
        if not self.plex_token:
            self.verify_pms_token()

        url = f"{self.base_url}:{self.port}/library/metadata/{rating_key}/refresh"
        payload = {}
        headers = {
            'Accept': 'application/json',
            "X-Plex-Token": self.plex_token}

        response = requests.request("PUT", url, headers=headers, data=payload)
        print(response.json())
