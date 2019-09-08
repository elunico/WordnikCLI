import curses


def center(text):
    return text.center(curses.COLS)


class ColorPairKind:
    WORD_PAIR = 1
    POS_PAIR = 2
    DEFN_PAIR = 3


class Screen:
    def __init__(self, win):
        self.win = win
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
        else:
            if state:
                self.attributes.add(curses.A_UNDERLINE)
            else:
                try:
                    self.attributes.remove(curses.A_UNDERLINE)
                except KeyError:
                    pass

    def invert(self, state=None):
        if state is None:
            return curses.A_STANDOUT in self.attributes
        else:
            if state:
                self.attributes.add(curses.A_STANDOUT)
            else:
                try:
                    self.attributes.remove(curses.A_STANDOUT)
                except KeyError:
                    pass

    def bold(self, state=None):
        if state is None:
            return curses.A_BOLD in self.attributes
        else:
            if state:
                self.attributes.add(curses.A_BOLD)
            else:
                try:
                    self.attributes.remove(curses.A_BOLD)
                except KeyError:
                    pass

    def color(self, kind):
        self._color = curses.color_pair(kind)

    def refresh(self):
        self.win.refresh()

    def subwin(self, *args, **kwargs):
        return self.win.subwin(*args, **kwargs)

    def getch(self, *args, **kwargs):
        return self.win.getch(*args, **kwargs)

    def addstr(self, s, centered=False):
        if centered:
            s = center(s)
        self.win.addstr(s, self.attrs())
