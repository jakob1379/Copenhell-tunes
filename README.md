# Copenhell tunes

<p align="center">
  <img src=".github/assets/lineup-to-playlist.svg" width="100%" alt="Pipeline diagram: a band is picked from the copenhell.dk line-up, found with Spotify artist search, its five most popular tracks are taken, and they are added to the playlist.">
</p>

A Python script that turns the announced Copenhell line-up into a Spotify playlist.
It reads the band names from the festival's program page, looks each band up on
Spotify, and fills a playlist you own with the top tracks of every band. It was
written for the Copenhell 2022 line-up.

## How it works

1. **Read the line-up.** Headless Firefox (via Selenium) loads
   `https://www.copenhell.dk/program#/artists/alphabetical`, and BeautifulSoup pulls
   out the artist names.
2. **Find each band.** Every name is searched on Spotify; the first artist hit is
   kept. A name with no hit is retried up to 8 times, then skipped.
3. **Take top tracks.** For each artist, the top tracks for one market (`DK` by
   default) are sorted by popularity and the first `n` (5 by default) are kept.
4. **Fill the playlist.** The playlist is emptied, then the tracks are added in
   batches of 100.

> [!WARNING]
> Running the script removes everything already in the target playlist.

The scraper matches the HTML class names of the copenhell.dk program page, so it
stops finding artists if the site's markup changes.

## Requirements

- Python 3.8 or newer
- Firefox and [geckodriver](https://github.com/mozilla/geckodriver) on your `PATH`
- A Spotify app from the [developer dashboard](https://developer.spotify.com/dashboard/applications),
  with your redirect URI added to its settings
- A public Spotify playlist you own. The script only asks for the
  `playlist-modify-public` scope.

## Install

```bash
git clone https://github.com/jakob1379/Copenhell-tunes.git
cd Copenhell-tunes
pip install -r requirements.txt selenium
```

`requirements.txt` does not list Selenium, so it is installed explicitly above.

## Credentials

The script needs four values. Each can come from a command-line flag, an
environment variable, or a `creds.json` file. A flag wins over an environment
variable, which wins over `creds.json`.

| Value         | Flag                  | Environment variable / `creds.json` key |
| ------------- | --------------------- | --------------------------------------- |
| Client ID     | `-i, --client-id`     | `CLIENT_ID`                             |
| Client secret | `-s, --client-secret` | `CLIENT_SECRET`                         |
| Redirect URI  | `-r, --redirect-uri`  | `REDIRECT_URI`                          |
| Playlist URI  | `-p, --playlist-uri`  | `PLAYLIST_URI`                          |

The client ID, secret and redirect URI are on your app's page at
`https://developer.spotify.com/dashboard/applications/<app_uri>`.

`creds.json` is read from the directory you run the script in, so put it in `src/`
(it is git-ignored there). The keys are upper case:

```json
{
  "CLIENT_ID": "<client_id>",
  "CLIENT_SECRET": "<client_secret>",
  "REDIRECT_URI": "https://localhost:8080",
  "PLAYLIST_URI": "<playlist_uri>"
}
```

## Usage

Run the script from `src/`:

```bash
cd src
python copenhell_bot.py
```

Change the market or the number of tracks per band with flags:

```bash
export PLAYLIST_URI="<playlist_uri>"
python copenhell_bot.py -c DK -n 3
```

On the first run Spotipy sends you through Spotify's sign-in to authorize the app
and caches the token in `src/.cache`.

```text
$ python copenhell_bot.py -h
usage: copenhell_bot.py [-h] [-i [CLIENT-ID]] [-s [CLIENT-SECRET]] [-r [REDIRECT-URI]]
                        [-p [PLAYLIST-URI]] [-c [country]] [-n [n-tracks]] [-q]

options:
  -h, --help            show this help message and exit
  -i, --client-id [CLIENT-ID]
                        Client id
  -s, --client-secret [CLIENT-SECRET]
                        Client secret
  -r, --redirect-uri [REDIRECT-URI]
                        Redirect uri from spotify dashboard settings
  -p, --playlist-uri [PLAYLIST-URI]
                        Playlist uri
  -c, --country [country]
                        Country to get top tracks from
  -n, --n-tracks [n-tracks]
                        Number of maximum tracks for each artist
  -q, --quiet           do not produce print anything
```

## License

Written by Jakob Guldberg Aaes. Released under the MIT License, see
[LICENSE.md](LICENSE.md).
