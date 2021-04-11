import json

from vyper import v

from plex import Plex
from radarr import Radarr
from tautulli import Tautulli

v.set_config_name("config")
v.add_config_path('.')
v.read_in_config()

SERVER_SETTINGS = v.get('servers')
BASE_URL = f"http://{SERVER_SETTINGS.get('base_ip')}"

radarr = Radarr(v.get('servers.radarr'), BASE_URL)
# SONARR_SETTINGS = v.get('servers.sonarr')
tautulli = Tautulli(v.get('servers.tautulli'), BASE_URL)
plex = Plex(v.get('servers.plex'), BASE_URL)


def delete_ignored_movies(threshold_in_days: int = 30):
    filtered_movies = set()

    ignored_movies = tautulli.get_ignored_movies(threshold_in_days)
    radar_movies = radarr.get_movies()
    print(len(ignored_movies))

    for movie in ignored_movies:
        movie_guid = tautulli.get_imdb_guid(movie['rating_key'])
        for r_movie in radar_movies:
            if not r_movie.get('imdbId'):
                filtered_movies.add((r_movie['title'], r_movie['id']))

            if r_movie.get('imdbId', None) == movie_guid:
                print(r_movie['imdbId'])
                filtered_movies.add((r_movie['title'], r_movie['id']))
    for filtered_movie in filtered_movies:
        print(f'Deleting {filtered_movie}')
        with open('deleted.log', 'a+') as file:
            file.write(f"{filtered_movie}\n")

        radarr.delete_movie(filtered_movie[1])



    return filtered_movies


if __name__ == '__main__':
    print(delete_ignored_movies(90))
