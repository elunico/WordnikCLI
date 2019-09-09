import curses


def parse_escape(s, idx):
    r = ''
    for i in range(idx, len(s)):
        if s[i] in '0123456789':
            r += s[i]
        else:
            break
    return r


class BufferedScreen:
    def __init__(self, win, lines, cols):
        self.win = win
        self.lines = lines
        self.cols = cols
        self.buffer = ''
        self.start = 0

    def moveup(self):
        self.start -= 1

    def movedown(self):
        self.start += 1

    def addstr(self, s, attrs):
        s.replace('%[', '%%[')
        self.buffer += "%[{}]{}".format(attrs, s)

    def render(self):
        result = ''
        lines = 0
        chars = 0
        attrs = {}
        i = 0
        # for i in range(len(self.buffer)):
        while i < len(self.buffer):
            c = self.buffer[i]
            if c == '%' and self.buffer[i+1] == '[':
                esc = parse_escape(self.buffer, i + 2)
                # 1 for ] and 2 for %[ plus length of integer
                i += len(esc) + 1 + 2
                # map the current index in result to the attrs int retrieved
                attrs[len(result)] = int(esc)
            else:
                if c == '\n':
                    chars = 0
                    lines += 1
                elif chars == self.cols-1:
                    lines += 1
                    chars = 0
                    result += '\n'
                result += c
                chars += 1
                i += 1
        self.win.clear()
        items = result.split('\n')
        try:
            ats = 0
            # FIXME: all of the attributes do not necessarily belong to the same line
            chcnt = sum(map(lambda s: len(s), items[:self.start]))
            for i in range(self.start, self.lines-1 + self.start):
                for idx in range(chcnt, chcnt + len(items[i])):
                    if idx in attrs:
                        ats = attrs[idx]
                self.win.addstr(items[i] + '\n', ats)
        except IndexError:
            pass


s = curses.initscr()
curses.noecho()
b = BufferedScreen(s, curses.LINES, curses.COLS)

for i in range(0, 500):
    b.addstr('line {}'.format(i), curses.A_STANDOUT if i %
             2 == 0 else curses.A_BOLD)

b.render()

while True:
    c = s.getch()
    if c == ord("u"):
        b.moveup()
    if c == ord("d"):
        b.movedown()
    if c == ord('q') or c == 10:
        break
    b.render()
curses.endwin()
