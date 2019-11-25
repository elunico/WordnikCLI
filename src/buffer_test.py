#!/usr/bin/python3

import unittest
from buffer import BufferedScreen
import curses

scr = curses.initscr()

b = BufferedScreen(scr, 10, 10)

b.addstr('This program uses BeautifulSoup, the Wordnik API (currently does scraping, but API use will be used in the future), requests (for python) to give')
b.render()
scr.getch()

curses.endwin()
