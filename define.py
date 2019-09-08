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
    pos_screen = scr.subwin(curses.LINES-2, right_start, 2, 4)
    defn_screen = scr.subwin(2, 4 + right_start)
    return (Screen(pos_screen, curses.LINES - 2, right_start),
            Screen(defn_screen, curses.LINES - 2, curses.COLS - right_start - 4))


def curses_end():
    scr.getch()
    curses.endwin()


def show_word_defintion(defn, pos_screen, defn_screen):
    pos, definition = defn

    pos_lines = 0
    defn_lines = 0

    pos_screen.underline(True)
    if pos != '':
        pos_screen.color(Colors.forKind('part-of-speech'))
        pos_lines += pos_screen.addstr(pos)
    else:
        pos_screen.color(Colors.forKind('missing-info'))
        pos_lines += pos_screen.addstr('<unknown>')

    defn_screen.color(Colors.forKind('definition'))
    defn_lines += defn_screen.addstr_wrapped(definition)

    pos_screen.refresh()
    defn_screen.refresh()

    return max([pos_lines, defn_lines])


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
    dict_entries = get_first_defintion(html)

    show_banner()
    show_requested_word(options.word)

    if dict_entries == []:
        rs = len('Error') + 2
        (pos_screen, defn_screen) = curses_create_subscrs(right_start=rs)
        show_not_found(pos_screen, defn_screen)
    else:
        [i if i[0] != '' else ('<unknown>', i[1]) for i in dict_entries]
        rs = len(max(dict_entries, key=lambda x: len(x[0]))[0]) + 2
        (pos_screen, defn_screen) = curses_create_subscrs(right_start=rs)
        lines = 0
        for entry in dict_entries:
            # TODO: make it scroll
            try:
                entry_lines = show_word_defintion(
                    entry, pos_screen, defn_screen)
                pos_screen.nl(entry_lines + 1)  # move down for next POS
                defn_screen.nl(2)  # move down a line for next definition
            except curses.error:
                break
            lines += entry_lines

    curses_end()


if __name__ == "__main__":
    main()
