import re
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from wrapt_timeout_decorator import timeout

# urls
BASE_URL = "https://www.copenhell.dk"
COPENHELL_RATE_LIMIT = 20

# TimeOuts
MAX_ARTIST_TIME = 30
MAX_URI_TIME = 120


def setup_browser(headless=True):
    """Initialize a Firefox (gecko) browser

    :param headless: Bool
                     Whether to run the browser headless or not
    :returns: selenium.webdriver.firefox.webdriver.WebDriver
              The browser

    """

    options = webdriver.FirefoxOptions()
    options.headless = headless
    options.add_argument("--window-size=1920x1080")
    driver = webdriver.Firefox(options=options)
    return driver


def unique(content):
    """Takes an iter and find the unique elements and return the simplified iter

    :param content: iter
                    Any iter that can be converted to a set
    :returns: iter
              an iter of same type but with only unique elements

    """

    the_type = type(content)
    return the_type(set(content))


def get_html_content():
    """Returns the HTML-code for thee line-up this years Copenhell

    :returns: str
              html content

    """

    lineup_url = BASE_URL + "/program#/artists/alphabetical"

    driver = setup_browser(headless=True)
    driver.get(lineup_url)
    sleep(10)
    driver.execute_script(
        "var scrollingElement = (document.scrollingElement || document.body);scrollingElement.scrollTop = scrollingElement.scrollHeight;"
    )
    sleep(5)
    html = driver.page_source
    driver.close()

    return html


def sort_name(name):
    """Extracts the first word that is not "the"

    :param names: List[str]
                  List of strings
    :returns: List[str]
              List of strings with

    """
    regex = re.compile(r"^the\ ")

    return regex.sub("", name.lower()).strip()


def extract_artist_info(html):
    """Takes the line-up html and extracts the artist names and their urls

    :param html: str
                 line-up html
    :returns: Tuple[List[str], List[str]]
              A tuple containing artist urls and artist names
    """


    soup = BeautifulSoup(html, features="html.parser")

    name_regex = re.compile(
        "gc-title gc__general-fonts-titles__font gc__components-thumbnail-overlayColorOver__color gc__components-thumbnail-overlayColor__background_before"
    )

    artist_names = unique(
        [name.get_text() for name in soup.find_all("span", {"class": name_regex})]
    )
    artist_names = [re.sub(r"\ \(.+\)", "", name).strip() for name in artist_names]

    # artist_url = BASE_URL + "/program{url}"
    # artist_tags = soup.find_all("a", href=re.compile(r"#/artist/.+"))
    # artist_urls = [
    #     artist_url.format(url=artist_tag.attrs["href"]) for artist_tag in artist_tags
    # ]

    return sorted(artist_names, key=sort_name)


@timeout(MAX_ARTIST_TIME)
def get_artist_names():
    """Return a list of artists sorted by name

    :returns: List[str]
              List of artists.

    """

    html = get_html_content()
    artist_names = extract_artist_info(html)
    return artist_names
