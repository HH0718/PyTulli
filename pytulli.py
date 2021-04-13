"""PyTulli is a script that allows a plex owner to leverage plex third party services like Tautulli, Radarr,
and Sonarr to find and delete ignored/unwatched movies and eventually TV shows. As of v2.0, PyTulli deletes movie
files based on n days from user input; any movie that was downloaded past n days AND has a null or 0 play_count will
be removed."""

from vyper import v

from services.plex import Plex
from services.radarr import Radarr
from services.tautulli import Tautulli

v.set_config_name("config")
v.add_config_path('.')
v.read_in_config()

SERVER_SETTINGS = v.get('servers')
BASE_URL = f"http://{SERVER_SETTINGS.get('base_ip')}"

plex = Plex(v.get('servers.plex'), BASE_URL)
radarr = Radarr(v.get('servers.radarr'), BASE_URL)
# SONARR_SETTINGS = v.get('servers.sonarr')
tautulli = Tautulli(v.get('servers.tautulli'), BASE_URL)


def delete_ignored_movies(threshold_in_days: int = 30) -> set:
    """Primary function of script. Requires an integer representing n days. Movies that have not been watched prior
    to n days will not be deleted."""
    filtered_movies = set()

    ignored_movies = tautulli.get_ignored_movies(threshold_in_days)
    radar_movies = radarr.get_movies()
    print(len(ignored_movies))  # Todo: convert to info level logging

    # todo: Simplify code block
    for movie in ignored_movies:
        movie_guid = tautulli.get_imdb_guid(movie['rating_key'])
        for r_movie in radar_movies:
            if not r_movie.get('imdbId'):
                filtered_movies.add((r_movie['title'], r_movie['id']))

            if r_movie.get('imdbId', None) == movie_guid:
                print(r_movie['imdbId'])
                filtered_movies.add((r_movie['title'], r_movie['id']))

    # Todo: consider dynamically adding to config file.
    for filtered_movie in filtered_movies:
        print(f'Deleting {filtered_movie}')
        with open('deleted.log', 'a+') as file:
            file.write(f"{filtered_movie}\n")

        radarr.delete_movie(filtered_movie[1])

    return filtered_movies


if __name__ == '__main__':
    print(delete_ignored_movies(90))
