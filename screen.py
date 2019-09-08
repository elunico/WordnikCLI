import curses


def center(text):
    return text.center(curses.COLS)


class ColorPairKind:

    @staticmethod
    def init_color_pairs():
        curses.init_pair(ColorPairKind.WORD_PAIR,
                         curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(ColorPairKind.POS_PAIR,
                         curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(ColorPairKind.DEFN_PAIR,
                         curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(ColorPairKind.ERROR_PAIR,
                         curses.COLOR_WHITE, curses.COLOR_RED)

    WORD_PAIR = 1
    POS_PAIR = 2
    DEFN_PAIR = 3
    ERROR_PAIR = 4


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

    def addstr_wrapped(self, s):
        msg = s.split(' ')
        c = 0
        for i in msg:
            string = i + ' '
            if len(string) + c > self.cols:
                self.win.addstr('\n\r', self.attrs())
                c = 0
            self.win.addstr(string, self.attrs())
            c += len(string)
