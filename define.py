#!/usr/bin/python3
import requests
import argparse
import curses
from bs4 import BeautifulSoup as bs
from web import *
from screen import Screen, center, ColorPairKind

scr = None


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('word', help='The word you want to define')
    return ap.parse_args()


def curses_setup(right_start):
    global scr
    scr = Screen(curses.initscr())
    curses.start_color()
    pos_screen = scr.subwin(2, 4)
    defn_screen = scr.subwin(2, 4 + right_start)
    curses.init_pair(ColorPairKind.WORD_PAIR,
                     curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(ColorPairKind.POS_PAIR,
                     curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(ColorPairKind.DEFN_PAIR,
                     curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    return Screen(pos_screen), Screen(defn_screen)


def curses_end():
    scr.getch()
    curses.endwin()


def main():
    options = parse_args()
    html = get_page_source_for_word(options.word)
    defn = get_first_defintion(html)

    rs = len(defn[0]) + 2
    (pos_screen, defn_screen) = curses_setup(right_start=rs)

    scr.invert(True)
    scr.addstr('define - Command Line Tool - define a word', centered=True)

    scr.invert(False)
    scr.bold(True)
    scr.addstr(options.word)

    pos_screen.underline(True)
    pos_screen.color(ColorPairKind.POS_PAIR)
    pos_screen.addstr(defn[0])

    defn_screen.color(ColorPairKind.DEFN_PAIR)
    defn_screen.addstr(defn[1])

    pos_screen.refresh()
    defn_screen.refresh()
    curses_end()


if __name__ == "__main__":
    main()
