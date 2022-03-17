import json
import re
from itertools import chain
from pathlib import Path
import requests
import spotipy
from bs4 import BeautifulSoup
from rich.progress import track
from spotipy.oauth2 import SpotifyOAuth
from wrapt_timeout_decorator import timeout

# urls
base_url = "https://www.roskilde-festival.dk"

# TimeOuts
max_artist_time = 20
max_uri_time = 120
max_top_track_time = 120

def load_credentials(fname='creds.json'):
    if Path(fname).is_file():
        with open(fname, "rb") as f:
            creds = json.load(f)
        return creds
    return {}


def setup_spotify_client(args):

    # Timeouts
    max_artist_time = 10  # seconds
    max_uri_time = 60

    # Spotify Client
    scope = ["playlist-modify-public"]

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=scope,
            client_id=args.client_id,
            client_secret=args.client_secret,
            redirect_uri=args.redirect_uri,
        )
    )
    return sp


@timeout(max_top_track_time)
def artists_top_tracks(artist_uris, client, country="DK", max_tracks=5, verbose=True):
    all_tracks = []
    for artist_uri in track(artist_uris):
        tracks = client.artist_top_tracks(artist_uri, country=country)["tracks"]
        tracks.sort(key=lambda track: track["popularity"], reverse=True)
        track_uris = [track["uri"].split(":")[-1] for track in tracks]
        all_tracks.extend(track_uris[:max_tracks])
    return all_tracks


def populate_playlist(tracks, playlist_uri, client, verbose=True):
    client.playlist_replace_items(playlist_uri, [])
    for i in track(range(0, len(tracks), 100), disable=(not verbose)):
        client.playlist_add_items(playlist_uri, tracks[i : i + 100])
