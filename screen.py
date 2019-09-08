import curses
import json
from math import ceil


def center(text):
    return text.center(curses.COLS)


def color_constant_for_name(name):
    prop = "COLOR_{}".format(name.upper())
    return getattr(curses, prop)


class Colors:

    # maps names to ints which get passed to curses.color_pair
    # since Screen#color() takes an int use this as follows
    # s = Screen(...)
    # s.color(Colors.forKind('error'))
    _colors = {}

    @staticmethod
    def forKind(kind):
        return curses.color_pair(Colors._colors[kind])

    @staticmethod
    def init_color_pairs():
        with open('colors.json') as f:
            clrs = json.load(f)['pairs']
            num = 1
            for (k, d) in clrs.items():
                curses.init_pair(num, color_constant_for_name(
                    d['foreground']), color_constant_for_name(d['background']))
                Colors._colors[k] = num
                num += 1


class Screen:
    def __init__(self, win, lines, cols):
        self.win = win
        self.lines = lines
        self.cols = cols
        self.attributes = set()
        self._color = None

    def attrs(self):
        a = 0
        for i in self.attributes:
            a |= i
        return a | (self._color if self._color else 0)

    def underline(self, state=None):
        if state is None:
            return curses.A_UNDERLINE in self.attributes
        elif state:
            self.attributes.add(curses.A_UNDERLINE)
        elif curses.A_UNDERLINE in self.attributes:
            self.attributes.remove(curses.A_UNDERLINE)

    def invert(self, state=None):
        if state is None:
            return curses.A_STANDOUT in self.attributes
        elif state:
            self.attributes.add(curses.A_STANDOUT)
        elif curses.A_STANDOUT in self.attributes:
            self.attributes.remove(curses.A_STANDOUT)

    def bold(self, state=None):
        if state is None:
            return curses.A_BOLD in self.attributes
        elif state:
            self.attributes.add(curses.A_BOLD)
        elif curses.A_BOLD in self.attributes:
            self.attributes.remove(curses.A_BOLD)

    def color(self, c):
        self._color = c

    def refresh(self):
        self.win.refresh()

    def subwin(self, *args, **kwargs):
        return self.win.subwin(*args, **kwargs)

    def getch(self, *args, **kwargs):
        return self.win.getch(*args, **kwargs)

    def nl(self, count=1):

        self.win.addstr('\n\r' * count)

    def addstr(self, s, centered=False):
        if centered:
            s = center(s)
        self.win.addstr(s, self.attrs())
        return ceil(len(s) / self.cols)

    def addstr_wrapped(self, s):
        msg = s.split(' ')
        lines = 1
        c = 0
        for i in msg:
            string = i + ' '
            if len(string) + c > self.cols:
                self.win.addstr('\n\r', self.attrs())
                c = 0
                lines += 1
            elif len(string) + c == self.cols:
                c = 0
                lines += 1
            self.win.addstr(string, self.attrs())
            c += len(string)
        return lines
