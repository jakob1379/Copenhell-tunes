import argparse
import os

from rich import print

import html_utils
from html_utils import get_artist_names
from spotify_utils import (
    artists_top_tracks,
    load_credentials,
    populate_playlist,
    setup_spotify_client,
    get_uris_from_names,
)


def fill_env_creds(args):
    """Fills the input args with credentials if not set through the cli. First it checks
    environmental variables and then the creds.json, where environmental takes precedence
    over creds.json

    :param args: argparse.Namespace
    :returns: argparse.Namespace

    """
    valid_tokens = ["CLIENT_ID", "CLIENT_SECRET", "REDIRECT_URI", "PLAYLIST_URI"]
    creds = load_credentials()

    for token in valid_tokens:
        if not getattr(args, token.lower()):
            if value := os.environ.get(token):
                setattr(args, token.lower(), value)
            elif value := creds.get(token):
                setattr(args, token.lower(), value)
    return args


def setup_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--client-id",
        help="Client id",
        type=str,
        nargs="?",
        default="",
        metavar="CLIENT-ID",
    )
    parser.add_argument(
        "-s",
        "--client-secret",
        help="Client secret",
        metavar="CLIENT-SECRET",
        type=str,
        nargs="?",
        default="",
    )
    parser.add_argument(
        "-r",
        "--redirect-uri",
        help="Redirect uri from spotify dashboard settings",
        metavar="REDIRECT-URI",
        type=str,
        nargs="?",
        default="",
    )
    parser.add_argument(
        "-p",
        "--playlist-uri",
        help="Playlist uri",
        metavar="PLAYLIST-URI",
        type=str,
        nargs="?",
        default="",
    )
    parser.add_argument(
        "-c",
        "--country",
        help="Country to get top tracks from",
        metavar="country",
        type=str,
        nargs="?",
        default="DK",
    )
    parser.add_argument(
        "-n",
        "--n-tracks",
        help="Number of maximum tracks for each artist",
        metavar="n-tracks",
        type=int,
        nargs="?",
        default=5,
    )
    parser.add_argument(
        "-q", "--quiet", help="do not produce print anything", action="store_true"
    )

    args = parser.parse_args()
    args = fill_env_creds(args)

    return args


def main():
    args = setup_args()

    # roskilde content section
    if not args.quiet:
        print("[bold cyan]Fetching artist uris from {html_utils.BASE_URL}[/bold cyan]")
    artist_names = get_artist_names()

    # # Spotify section
    if not args.quiet:
        print("[bold cyan]Fetching artist uris from names through Spotify")
    spotify_client = setup_spotify_client(args)
    artist_uris = get_uris_from_names(
        artist_names, spotify_client, verbose=(not args.quiet)
    )

    if not args.quiet:
        print("[bold cyan]Fetching artist top tracks[/bold cyan]")
    top_tracks = artists_top_tracks(
        artist_uris,
        spotify_client,
        country=args.country,
        max_tracks=args.n_tracks,
        verbose=(not args.quiet),
    )

    if not args.quiet:
        print("[bold cyan]Adding tracks to playlist[/bold cyan]")
    populate_playlist(
        top_tracks, args.playlist_uri, spotify_client, verbose=(not args.quiet)
    )

    print("[bold green]Done![/bold green]")


if __name__ == "__main__":
    main()
