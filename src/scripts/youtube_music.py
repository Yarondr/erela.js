import sys
from typing import List

from spotdl.providers import ytm_provider
from ytmusicapi import YTMusic

ytmusic = YTMusic()


def get_song(song_name: str, song_artists: List[str], song_album_name: str, song_duration: int):
    song_title = create_song_title(song_name, song_artists).lower()

    # Query YTM by songs only first
    song_results = query_and_simplify(song_title, "songs")

    songs = ytm_provider._order_ytm_results(
        song_results,
        song_name,
        song_artists,
        song_album_name,
        song_duration
    )

    if len(songs) != 0:
        best_result = max(songs, key=lambda k: songs[k])

        if songs[best_result] >= 80:
            return best_result

    # Didn't find the current song when searching for songs, now we will try to search videos
    video_results = query_and_simplify(song_title, filter="videos")

    videos = ytm_provider._order_ytm_results(
        video_results,
        song_name,
        song_artists,
        song_album_name,
        song_duration
    )

    results = {**songs, **videos}

    if len(results) == 0:
        return None

    results_items = list(results.items())

    sorted_results = sorted(results_items, key=lambda x: x[1], reverse=True)

    return sorted_results[0][0]


def query_and_simplify(search_term: str, filter: str) -> List[dict]:
    search_results = ytmusic.search(search_term, filter=filter)
    return list(map(_map_result_to_song_data, search_results))


def _map_result_to_song_data(result: dict) -> dict:
    artists = ", ".join(map(lambda a: a["name"], result["artists"]))
    video_id = result["videoId"]

    # Ignore results without video id
    if video_id is None:
        return {}

    song_data = {
        "name": result["title"],
        "type": result["resultType"],
        "artist": artists,
        "length": _parse_duration(result.get("duration", None)),
        "link": f"https://www.youtube.com/watch?v={video_id}",
    }

    album = result.get("album")
    if album:
        song_data["album"] = album["name"]

    return song_data


def create_song_title(song_name: str, song_artists: List[str]) -> str:
    joined_artists = ", ".join(song_artists)
    return f"{joined_artists} - {song_name}"


def _parse_duration(duration: str) -> float:
    """
    Convert string value of time (duration: "25:36:59") to a float value of seconds (92219.0)
    """
    try:
        # {(1, "s"), (60, "m"), (3600, "h")}
        mapped_increments = zip([1, 60, 3600], reversed(duration.split(":")))
        seconds = 0
        for multiplier, time in mapped_increments:
            seconds += multiplier * int(time)

        return float(seconds)

    # ! This usually occurs when the wrong string is mistaken for the duration
    except (ValueError, TypeError, AttributeError):
        return 0.0