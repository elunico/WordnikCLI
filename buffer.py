import curses


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

    def addstr(self, s):
        self.buffer += s

    def render(self):
        result = ''
        lines = 0
        chars = 0
        for c in self.buffer:
            if c == '\n':
                chars = 0
                lines += 1
            elif chars == self.cols-1:
                lines += 1
                chars = 0
                result += '\n'
            result += c
            chars += 1
        self.win.clear()
        items = result.split('\n')
        try:
            for i in range(self.start, self.lines-1 + self.start):
                self.win.addstr(items[i] + '\n')
        except IndexError:
            pass


s = curses.initscr()
curses.noecho()
b = BufferedScreen(s, curses.LINES, curses.COLS)

for i in range(0, 500):
    b.addstr('line {}'.format(i))

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
