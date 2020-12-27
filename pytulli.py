"""Parses Tautulli video library for date added and play count, then directly deletes movies from Plex movie
folders."""

__author__ = '/u/Return_Foo_Bar'
__version__ = 2.0

from vyper import v

v.set_config_name('config')
v.add_config_path('.')
v.read_in_config()

config = v
