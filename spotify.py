import os

import youtube_music

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from urllib.parse import urlparse

def get_track_yt_url(track_id: str):
    urn = "spotify:track:" + track_id
    track = spotify.track(urn)

    song_name = track['name']
    artists = []
    for artist in track['artists']:
        artists.append(artist['name'])
    album_name = track['album']['name']
    song_duration = round(track['duration_ms']/1000, ndigits=3)

    return youtube_music.get_song(song_name, artists, album_name, song_duration)


def get_playlist_yt_urls(playlist_id: str):
    pl_id = "spotify:playlist:" + playlist_id
    offset = 0
    urls = []

    get_playlist_title(playlist_id)

    while True:
        response = spotify.playlist_items(pl_id, offset=offset, fields='items.track.id,total', additional_types=['track'])

        if len(response['items']) == 0:
            break

        offset += len(response['items'])
        for track in response['items']:
            urls.append(get_track_yt_url(track['track']['id']))
    return [urls, get_playlist_title(playlist_id)]


def get_playlist_title(playlist_id: str):
    pl_id = "spotify:user:spotifycharts:playlist:" + playlist_id
    playlist = spotify.playlist(pl_id)
    return playlist['name']


def get_album_yt_urls(album_id: str):
    urn = "spotify:album:" + album_id
    album = spotify.album(urn)
    urls = []
    for track in album['tracks']['items']:
        urls.append(get_track_yt_url(track['id']))
    return [urls, album['name']]


def get_artist_top_tracks(artist_id: str):
    urn = "spotify:artist:" + artist_id
    top_tracks = spotify.artist_top_tracks(urn)
    artist = spotify.artist(urn)
    urls = []
    for track in top_tracks['tracks']:
        urls.append(get_track_yt_url(track['id']))
    print(artist['name'])
    return [urls, artist['name']]


def get_songs_urls(songs_url: str):
    song_type = get_type(songs_url)
    if song_type[0] == "track":
        return [get_track_yt_url(song_type[1])]
    elif song_type[0] == "playlist":
        return get_playlist_yt_urls(song_type[1])
    elif song_type[0] == "album":
        return get_album_yt_urls(song_type[1])
    elif song_type[0] == "artist":
        return get_artist_top_tracks(song_type[1])


def get_type(url: str):
    query = urlparse(url)
    if query.path.startswith("/track"):
        return ['track', query.path.split("/track/")[1]]
    elif query.path.startswith("/playlist"):
        return ['playlist', query.path.split("/playlist/")[1]]
    elif query.path.startswith("/album"):
        return ['album', query.path.split("/album/")[1]]
    elif query.path.startswith("/artist"):
        return ['artist', query.path.split("/artist/")[1]]
    
if __name__ == "__main__":
    args = os.sys.argv[1:]
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
        client_id=args[0], client_secret=args[1]))
    print(get_songs_urls(args[2]))
    