from dataclasses import dataclass


@dataclass
class Movie:
    title: str = None
    sort_title: str = None
    rating_key: int = 0
    year: int = 0
    added_at: int = 0
    last_played: int = 0
    play_count: int = 0
