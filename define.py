#!/usr/bin/python3
import requests
import argparse
import curses
from bs4 import BeautifulSoup as bs
from web import *
from screen import Screen, center, Colors

scr = None


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('word', help='The word you want to define')
    return ap.parse_args()


def curses_begin():
    global scr
    scr = Screen(curses.initscr(), curses.LINES, curses.COLS)
    curses.start_color()
    Colors.init_color_pairs()


def curses_create_subscrs(right_start):
    pos_screen = scr.subwin(2, 4)
    defn_screen = scr.subwin(2, 4 + right_start)
    return (Screen(pos_screen, curses.LINES - 2, right_start - 1 - 4),
            Screen(defn_screen, curses.LINES - 2, curses.COLS - right_start - 4))


def curses_end():
    scr.getch()
    curses.endwin()


def show_word_defintion(defn, pos_screen, defn_screen):
    pos, definition = defn

    pos_screen.underline(True)
    pos_screen.color(Colors.forKind('part-of-speech'))
    pos_screen.addstr(pos)

    defn_screen.color(Colors.forKind('definition'))
    defn_screen.addstr_wrapped(definition)

    pos_screen.refresh()
    defn_screen.refresh()


def show_not_found(pos_screen, defn_screen):
    pos_screen.color(Colors.forKind('error'))
    pos_screen.addstr("Error")

    defn_screen.color(Colors.forKind('error'))
    defn_screen.addstr_wrapped("Could not find a defition for the given word!")
    defn_screen.nl()
    defn_screen.bold(True)
    defn_screen.addstr_wrapped("Note that Wordnik is case-sensitive")

    pos_screen.refresh()
    defn_screen.refresh()


def show_banner():
    scr.invert(True)
    scr.addstr('define - Command Line Tool - define a word', centered=True)


def show_requested_word(word):
    scr.invert(False)
    scr.bold(True)
    scr.addstr(word)


def main():

    curses_begin()

    options = parse_args()
    html = get_page_source_for_word(options.word)
    defn = get_first_defintion(html)

    show_banner()
    show_requested_word(options.word)

    if defn is None:
        rs = len('Error') + 2
        (pos_screen, defn_screen) = curses_create_subscrs(right_start=rs)
        show_not_found(pos_screen, defn_screen)
    else:
        rs = len(defn[0]) + 2
        (pos_screen, defn_screen) = curses_create_subscrs(right_start=rs)
        show_word_defintion(defn, pos_screen, defn_screen)

    curses_end()


if __name__ == "__main__":
    main()
