"""Parses Tautulli video library for date added and play count, then directly deletes movies from Plex movie
folders. """

__author__ = '/u/Return_Foo_Bar'
__version__ = '0.1'

import configparser
import os

import paramiko as paramiko
import pendulum
import requests

# Read config file
config = configparser.ConfigParser()
config.read('config.ini')

DEBUG = config['MISC']['DEBUG']
DAYS = int(config['MISC']['DAYS'])

# Tautulli config
API_KEY = config['TAUTULLI']['API_KEY']
API_ENDPOINT = config['TAUTULLI']['API_ENDPOINT']

# Plex Server config
SERVER = config['PLEX_SERVER_SSH']['SERVER']
PORT = config['PLEX_SERVER_SSH']['PORT']
USERNAME = config['PLEX_SERVER_SSH']['USERNAME']
PASSWORD = config['PLEX_SERVER_SSH']['PASSWORD']
PLEX_MOVIE_ROOT = config['MISC']['PLEX_MOVIE_ROOT']
SECTION_ID = config['MISC']['SECTION_ID']

# connect to Plex Server via SSH
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
ssh.connect(SERVER, port=PORT, username=USERNAME, password=PASSWORD)


def remove_movies(movie_path_list):
    """Deletes files in each `movie_path_List` and then removes the movie directory. Then logs status of movie files."""
    paths = movie_path_list
    sftp = ssh.open_sftp()
    with open('movie_removed.example.log', 'a') as log_file:
        if DEBUG:
            log_file.write(f"{'*' * 19}\n")
            log_file.write(f"{'*' * 5}  DEBUG  {'*' * 5}\n")
            log_file.write(f"{'*' * 19}\n\n")

        for path in paths:
            log_file.write(f"{'*' * 5}  {path}  {'*' * 5}\n")
            single_path = os.path.join(PLEX_MOVIE_ROOT, path)
            files_in_movie_path = sftp.listdir(path=single_path)

            for file in files_in_movie_path:
                if not DEBUG:
                    try:
                        sftp.remove(single_path + file)
                        log_file.write(f"'{file}' successfully removed\n")
                    except:  # Haven't figured out exceptions yet.
                        log_file.write(f"Failed to remove '{file}'\n")
                else:
                    log_file.write(f"File '{file}' would have been removed\n")

            if not DEBUG:
                try:
                    sftp.rmdir(single_path)
                    log_file.write(f"'{single_path}' successfully removed\n")
                    log_file.write("\n\n\n")

                except:  # Haven't figured out exceptions yet.
                    log_file.write(f"Failed to remove {single_path}\n")
                    log_file.write("\n\n\n")
            else:
                log_file.write(f"Folder '{single_path}', would have been removed\n")
                log_file.write("\n\n\n")

    sftp.close()


def not_played_in_n_days(days, last_played):
    """Returns `True` if movie has been played in n days. """
    today = pendulum.now()
    if today.diff(pendulum.from_timestamp(int(last_played))).in_days() > days:
        return True





def main():
    num_of_forgotten_movies = 0

    # Get movie library data
    movies = get_movie_library()
    forgotten_movies_list = []
    movie_folders = []

    # Determine if movies are forgotten. If so, add to `forgotten_movies_list`.
    for movie in movies["response"]["data"]["data"]:
        if (movie['play_count'] is not None and not_played_in_n_days(DAYS, movie['last_played'])) or \
                (movie['play_count'] is None and not_played_in_n_days(DAYS, movie['added_at'])):
            forgotten_movies_list.append(movie)
            num_of_forgotten_movies += 1
    if num_of_forgotten_movies == 0:
        print("No forgotten movies found.")
        exit()

    # get movie folder path on plex server to delete
    for movie in forgotten_movies_list:
        metas = get_metadata(movie["rating_key"])
        try:
            for meta in metas["response"]["data"]["media_info"]:
                parts = (meta["parts"])
                for part in parts:
                    path = part["file"].split('/', 4)[3:4]
                    movie_folders.append(path[0])

        except:  # Still learning exceptions
            pass

    remove_movies(movie_folders)

    ssh.close()

    refresh_libraries_list()


main()
