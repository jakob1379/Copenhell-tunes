import re
from itertools import chain

import requests
from bs4 import BeautifulSoup
from ratelimiter import RateLimiter
from rich.progress import track
from wrapt_timeout_decorator import timeout

# urls
BASE_URL = "https://www.roskilde-festival.dk"
ROSKILDE_RATE_LIMIT = 20

# TimeOuts
MAX_ARTIST_TIME = 20
MAX_URI_TIME = 120


@timeout(MAX_ARTIST_TIME)
def get_artist_urls():
    lineup_url = BASE_URL + "/da/line-up/"
    lineup_content = requests.get(lineup_url).content
    soup = BeautifulSoup(lineup_content, features="html.parser")

    artist_tags = soup.find_all("a", href=re.compile(r"/da/years/2022/acts/"))
    artist_urls = [
        artist_tag.attrs["href"]
        for artist_tag in artist_tags
        if "href" in artist_tag.attrs
    ]

    return artist_urls


@timeout(MAX_URI_TIME)
@RateLimiter(max_calls=ROSKILDE_RATE_LIMIT, period=1)
def get_uris_from_urls(artist_urls, verbose=True):
    uri_from_url = re.compile(r"\/artist\/([a-zA-Z0-9]+)+\?si=")
    spotify_uris = []

    for artist_url in track(artist_urls, disable=(not verbose)):
        artist_content = requests.get(BASE_URL + artist_url).content
        soup = BeautifulSoup(artist_content, features="html.parser")

        iframes = soup.find_all(
            "iframe", {"data-src": re.compile(r"open\.spotify\.com")}
        )

        spotify_uris.extend(
            chain(
                *[
                    uri_from_url.findall(frame.attrs["data-src"])
                    for frame in iframes
                    if "data-src" in frame.attrs
                ]
            )
        )

    return spotify_uris
