import requests
import sys
import argparse
from bs4 import BeautifulSoup as bs, NavigableString as ns


SEARCH_PAGES_URL = 'https://en.wiktionary.org/w/api.php?action=query&format=json&list=search&utf8=1&srsearch={query}'


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('word', help="The word to lookup")
    ap.add_argument('-p', '--plaintext', action='store_true',
                    help='Display the entire wiktionary entry in plaintext')
    return ap.parse_args()


def escape(q):
    return q.replace(' ', '%20')


def check_response(res):
    msg = "Failed to fetch search results page: " + str(res.reason)
    if res.status_code != 200:
        raise ConnectionError(msg)


def get_pageid_for_word(word):
    r = requests.get(SEARCH_PAGES_URL.format(query=escape(word)))
    check_response(r)
    results = r.json()
    return results['query']['search'][0]['pageid']


PAGE_SECTIONS_URL = 'https://en.wiktionary.org/w/api.php?action=parse&format=json&pageid={pageid}&prop=sections'


def get_english_section_num_for_pageid(pageid):
    r = requests.get(PAGE_SECTIONS_URL.format(pageid=pageid))
    check_response(r)
    res = r.json()
    sections = res['parse']['sections']
    for i in range(len(sections)):
        section = sections[i]
        if section['line'].lower() == 'english':
            return i + 1  # wiktionary sections start at 1


PAGE_TEXT_URL = 'https://en.wiktionary.org/w/api.php?action=query&format=json&prop=extracts&pageids={pageid}&redirects=1&explaintext=1&exsectionformat=plain'


def get_text_for_pageid(pageid):
    r = requests.get(PAGE_TEXT_URL.format(pageid=pageid))
    check_response(r)
    res = r.json()
    text = res['query']['pages'][str(pageid)]['extract']
    return text


SECTION_HTML_URL = 'https://en.wiktionary.org/w/api.php?action=parse&format=json&pageid={pageid}&prop=text&section={sectionid}&disabletoc=1'


def get_html_for_pageid_and_sectionid(pageid, sectionid):
    r = requests.get(SECTION_HTML_URL.format(
        pageid=pageid, sectionid=sectionid))
    check_response(r)
    res = r.json()
    html = res['parse']['text']['*']
    return html


def parse_html_to_definitions(html):
    soup = bs(html, 'html5lib')
    lists = soup.find_all('ol')
    defn_list = lists[0]
    items = defn_list.find_all('li')
    for item in items:
        if not isinstance(item, ns):
            print(item.text)


def main():
    options = parse_args()

    word = options.word
    try:
        pageid = get_pageid_for_word(word)
        if options.plaintext:
            text = get_text_for_pageid(pageid)
            print(text)
        else:
            sectionid = get_english_section_num_for_pageid(pageid)
            html = get_html_for_pageid_and_sectionid(pageid, sectionid)
            definitions = parse_html_to_definitions(html)
            print(definitions)

    except ConnectionError as e:
        print(e)
        exit(2)


if __name__ == "__main__":
    main()
