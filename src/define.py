#!/usr/bin/python3
import requests
import argparse
import curses
from bs4 import BeautifulSoup as bs
from web import *
from screen import Screen, center, Colors
from debug import dump_locals, dump_obj

scr = None


def show_keybindings():
    curses_begin()
    show_banner()
    show_requested_word('Keybindings')
    scr.refresh()
    dict_entries = [
        ('<escape>', "exit the program"),
        ('q', 'exit the program'),
        ('<enter>', 'Move down one line'),
        ('<down arrow>', 'Move down one line'),
        ('<up arrow>', "Move up one line"),
        ('r -> x', "(Press r then press x) Enter debug mode"),
        ('w', 'Debug mode only: move the left column up one line'),
        ('e', 'Debug mode only: move the right column up one line'),
        ('s', 'Debug mode only: move the left column down one line'),
        ('d', 'Debug mode only: move the right column down one line'),
    ]
    rs = len(max(dict_entries, key=lambda x: len(x[0]))[0]) + 2
    (pos_screen, defn_screen) = curses_create_subscrs(right_start=rs)
    lines = 0
    for entry in dict_entries:
        entry_lines = show_word_defintion(
            entry, pos_screen, defn_screen)
        pos_screen.nl(entry_lines + 1)
        defn_screen.nl(2)
        lines += entry_lines

    curses_end(pos_screen, defn_screen)


def parse_args():
    ap = argparse.ArgumentParser(
        usage='usage: define.py (-h | -k | word [word ...]) [-t]',
        description="A program for defining words in the terminal. "
        "Definitions provided by https://www.wordnik.com/"
    )
    ap.add_argument('word', nargs='*', help='The word you want to define')
    ap.add_argument('-k', '--keybindings', action="store_true",
                    help='Show the keybindings used by the program and exit')
    ap.add_argument('-t', '--traceback', action="store_true", required=False,
                    help=('Instead of using the default message on '
                          'network failure (which is to display "No '
                          'defintions found") instead raise an '
                          'exception with the reason for the network'
                          ' failure'))
    options = ap.parse_args()
    if not options.keybindings and not options.word:
        ap.error("You must specify at least one word "
                 "to define or the -k flag or the -h flag")

    return options


def curses_begin():
    global scr
    scr = Screen(curses.initscr(), curses.LINES, curses.COLS)
    curses.noecho()
    scr.win.keypad(1)
    curses.start_color()
    Colors.init_color_pairs()


def curses_create_subscrs(right_start):
    pos_screen = scr.subwin(curses.LINES-2, right_start, 2, 4)
    defn_screen = scr.subwin(2, 4 + right_start)
    return (Screen(pos_screen, curses.LINES - 2, right_start),
            Screen(defn_screen, curses.LINES - 2, curses.COLS - right_start - 4))


prev = None
allow_separate = False


def curses_mainloop(pos_screen, defn_screen):
    global allow_separate
    global prev
    while True:
        c = scr.getch()
        if c == ord('r'):
            prev = c
        if c == ord('x') and prev == ord('r'):
            allow_separate = True
        if allow_separate:
            if c == ord('w'):
                pos_screen.moveup()
            if c == ord('s'):
                pos_screen.movedown()
            if c == ord('e'):
                defn_screen.moveup()
            if c == ord('d'):
                defn_screen.movedown()
        if c == 262:
            pos_screen.top()
            defn_screen.top()
        if c == 360:
            pos_screen.bottom()
            defn_screen.bottom()
        if c == 338:
            pos_screen.movedown(pos_screen.lines)
            defn_screen.movedown(defn_screen.lines)
        if c == 339:
            pos_screen.moveup(pos_screen.lines)
            defn_screen.moveup(defn_screen.lines)
        if c == 259:
            pos_screen.moveup()
            defn_screen.moveup()
        if c == 258 or c == 10:
            pos_screen.movedown()
            defn_screen.movedown()
        if c == ord('q') or c == 27:
            break
        pos_screen.refresh()
        defn_screen.refresh()


def show_word_defintion(defn, pos_screen, defn_screen):
    pos, definition = defn

    pos_lines = 0
    defn_lines = 0

    pos_screen.underline(True)
    if pos == '<unknown>':
        pos_screen.color(Colors.forKind('missing-info'))
    else:
        pos_screen.color(Colors.forKind('part-of-speech'))

    pos_lines += pos_screen.addstr(pos)

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
    global pos_screen, defn_screen
    options = parse_args()
    if options.keybindings:
        try:
            show_keybindings()
            return
        except:
            curses.endwin()
            raise

    curses_begin()
    word = ' '.join(options.word)
    try:
        html = get_page_source_for_word(word)
        dict_entries = get_all_definitions(html)
    except ConnectionError:
        if options.traceback:
            curses.endwin()
            raise
        dict_entries = []

    if word == 'potato':
        dict_entries = [('noun', '❤️')] + dict_entries

    show_banner()
    show_requested_word(word)
    scr.refresh()

    if dict_entries == []:
        rs = len('Error') + 2
        (pos_screen, defn_screen) = curses_create_subscrs(right_start=rs)
        show_not_found(pos_screen, defn_screen)
    else:
        dict_entries = [
            i if i[0] != '' else ('<unknown>', i[1]) for i in dict_entries
        ]
        rs = len(max(dict_entries, key=lambda x: len(x[0]))[0]) + 2
        (pos_screen, defn_screen) = curses_create_subscrs(right_start=rs)
        lines = 0
        for entry in dict_entries:
            # try:
            entry_lines = show_word_defintion(
                entry, pos_screen, defn_screen)
            pos_screen.nl(entry_lines + 1)  # move down for next POS
            defn_screen.nl(2)  # move down a line for next definition
            # except curses.error:
            # break
            lines += entry_lines

    curses_mainloop(pos_screen, defn_screen)
    curses.endwin()


if __name__ == "__main__":
    main()
