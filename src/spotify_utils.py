import json
from pathlib import Path
from time import sleep

import spotipy
from ratelimiter import RateLimiter
from rich import print
from rich.progress import track
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth
from wrapt_timeout_decorator import timeout

# TimeOuts
MAX_ARTIST_TIME = 20
MAX_URI_TIME = 120
MAX_TOP_TRACK_TIME = 120
COPENHELL_RATE_LIMIT = 20


def load_credentials(fname="creds.json"):
    """Load credentials from file

    :param fname:
    :returns:

    """

    if Path(fname).is_file():
        with open(fname, "rb") as f:
            creds = json.load(f)
        return creds
    return {}


def setup_spotify_client(args):
    """Sets up a Spotify client using the credentials

    :param args: argparse.Namespace
    :returns: spotipy.client.Spotify
              Spotify client

    """
    scope = ["playlist-modify-public"]

    spotify = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=scope,
            client_id=args.client_id,
            client_secret=args.client_secret,
            redirect_uri=args.redirect_uri,
        )
    )
    return spotify


@timeout(MAX_URI_TIME)
@RateLimiter(max_calls=COPENHELL_RATE_LIMIT, period=1)
def get_uris_from_names(artist_names, client, verbose=True, max_retries:int = 8):
    """Uses the Spotify API to get the artists Spotify-URI solely based on names. If no
    artist is found there will be `max_retries` retries before abandoning the artist.

    :param artist_names: List[str]
                         List with artist names
    :param client: spotipy.client.Spotify
                   Spotify client
    :param verbose: bool
                    Should there be any visual output to the command line
    :param max_retries: int
                        Max number of retries before continuing to next artist
    :returns: List[str]
              List of artist-URIs

    """

    artist_uris = []

    for name in track(artist_names, disable=(not verbose)):
        for i in range(max_retries):
            try:
                ans = client.search(q=f"artist:{name.lower()}", type="artist", limit=1)
                if not ans["artists"].get("items"):
                    print(
                        f"[yellow]Warning: No artist found for {name} - retrying {i+1}/{max_retries}[/yellow]"
                    )
                    sleep(0.5)
                    continue
                if artists := ans["artists"].get("items"):
                    print(f"[green]Found artist: {name}[/green]")
                    artist_uri = artists[0]["uri"]
                    artist_uris.append(artist_uri)
                    break
            except Exception as err:
                if verbose:
                    print(f"[yellow]Error: {name}[/yellow]")
                    print(f"[yellow]{err}[/yellow]")
    return artist_uris


@timeout(MAX_TOP_TRACK_TIME)
def artists_top_tracks(artist_uris, client, country="DK", max_tracks=5, verbose=True):
    """Find top tracks for each artist

    :param artist_uris: List[str]
                        List of artist uris
    :param client: spotipy.client.Spotify
                   Spotify client
    :param country: str
                    Market identifier as top tracks changes the top tracks
    :param max_tracks: int
                       Max number of tracks for each artist
    :param verbose: bool
                    Output messages to commandline
    :returns: List[str]
              List of track URIs
    """

    all_tracks = []
    for artist_uri in track(artist_uris, disable=(not verbose)):
        tracks = client.artist_top_tracks(artist_uri, country=country)["tracks"]
        tracks.sort(key=lambda track: track["popularity"], reverse=True)
        track_uris = [track["uri"].split(":")[-1] for track in tracks]
        all_tracks.extend(track_uris[:max_tracks])
    return all_tracks


def populate_playlist(tracks, playlist_uri, client, verbose=True):
    """Insert track uris into a playlist

    :param tracks: List[str]
                   List of track URIs
    :param playlist_uri: str
                         The playlist URI
    :param client: spotipy.client.Spotify
                   Spotify client
    :param verbose: bool
                    Output messages to commandline
    :returns: None
    """

    client.playlist_replace_items(playlist_uri, [])
    for i in track(range(0, len(tracks), 100), disable=(not verbose)):
        client.playlist_add_items(playlist_uri, tracks[i : i + 100])
