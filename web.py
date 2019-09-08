import requests
from bs4 import BeautifulSoup as bs

BASE_URL = 'https://www.wordnik.com/words/{}'


def get_page_source_for_word(word):
    r = requests.get(BASE_URL.format(word))
    if r.status_code != 200:
        raise ConnectionError(r.reason)
    return r.content


def get_first_defintion(html):
    tree = bs(html, 'html5lib')
    container = tree.find('div', id='define')
    item = container.find('li')
    if item is None:
        return None
    # TODO: get all li's make subwins for every one? and add all defintions and POSes
    part = item.find('abbr')
    part.extract()
    return part.text.strip(), item.text.strip()
