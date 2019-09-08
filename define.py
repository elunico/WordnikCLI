import requests
import argparse
import curses
from bs4 import BeautifulSoup as bs

scr = None
BASE_URL = 'https://www.wordnik.com/words/{}'
WORD_PAIR = 1
POS_PAIR = 2
DEFN_PAIR = 3


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('word', help='The word you want to define')
    return ap.parse_args()


def get_page_source_for_word(word):
    r = requests.get(BASE_URL.format(word))
    if r.status_code != 200:
        raise ConnectionError(r.reason)
    return r.content


def get_first_defintion(html):
    tree = bs(html, 'html5lib')
    container = tree.find('div', id='define')
    item = container.find('li')
    part = item.find('abbr')
    part.extract()
    return part.text.strip(), item.text.strip()


def curses_setup(right_start):
    global scr
    scr = curses.initscr()
    curses.start_color()
    pos_screen = scr.subwin(2, 4)
    defn_screen = scr.subwin(2, 4 + right_start)
    curses.init_pair(WORD_PAIR, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(POS_PAIR, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(DEFN_PAIR, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    return pos_screen, defn_screen


def curses_end():
    scr.getch()
    curses.endwin()


def center(text):
    return text.center(curses.COLS)


def main():
    options = parse_args()
    html = get_page_source_for_word(options.word)
    defn = get_first_defintion(html)

    rs = len(defn[0]) + 2
    (pos_screen, defn_screen) = curses_setup(right_start=rs)

    title = center('define - Command Line Tool - define a word')
    scr.addstr(title, curses.A_STANDOUT)
    scr.addstr(options.word, curses.A_BOLD | curses.color_pair(WORD_PAIR))

    pos_screen.addstr(defn[0], curses.A_UNDERLINE |
                      curses.color_pair(POS_PAIR))
    defn_screen.addstr(defn[1], curses.color_pair(DEFN_PAIR))

    pos_screen.refresh()
    defn_screen.refresh()
    curses_end()


if __name__ == "__main__":
    main()
