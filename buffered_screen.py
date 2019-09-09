import curses


class BufferedScreen:
    def __init__(self, win, lines, cols):
        self.win = win
        self.lines = lines
        self.cols = cols
        self.buffer = []
        self.start = 0
        self.cur_lines = 0
        self.cur_chars = 0

    def transform(self, s):
        result = []
        temp = ''
        for c in s:
            if c == '\r':
                continue
            if c == '\n':
                result.append(temp + '\n')
                temp = ''
            else:
                temp += c
        if temp:
            result.append(temp)
        return result

    def count_lines(self, s):
        self.cur_lines += s.count('\n')
        self.cur_chars += len(s)
        if self.cur_chars > self.cols:
            self.cur_lines += self.cur_chars // self.cols
            self.cur_chars = self.cur_chars % self.cols

    def addstr(self, s, attr):
        self.count_lines(s)
        for s in self.transform(s):
            self.buffer.append((s, attr))

    def render(self):
        self.win.clear()
        i = self.start
        lines = 0
        chars = 0
        # FIXME:
        # screen avoids using last line?? or last two ??
        # screen blows past bounds when going down
        while lines < min(self.lines, self.cur_lines):
            self.win.addstr(self.buffer[i][0], self.buffer[i][1])
            # if the line is long enough to wrap, it counts as a new line
            # as do all '\n'
            lines += self.buffer[i][0].count('\n')
            chars += len(self.buffer[i][0])

            if chars > self.cols:
                lines += chars // self.cols
                chars = chars % self.cols

            i += 1

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except:
            return self.win.__getattribute__(name)

    def move_down(self):
        if self.start < self.cur_lines - self.lines:
            self.start += 1

    def move_up(self):
        if self.start > 0:
            self.start -= 1

    def listen(self):
        active = True
        while active:
            ch = screen.getch()
            if ch == 27:
                ch = screen.getch()
                if ch == 91:
                    ch = screen.getch()
                    if ch == 65:
                        buffer.move_up()
                    elif ch == 66:
                        buffer.move_down()
            if ch == 117:
                buffer.move_up()
            elif ch == 100:
                buffer.move_down()
            elif ch == 113 or ch == 10:
                active = False
            buffer.render()


screen = curses.initscr()
curses.noecho()
screen.scrollok(True)
screen.idlok(True)
buffer = BufferedScreen(screen, curses.LINES, curses.COLS)

for i in range(0, 50, 2):
    buffer.addstr('Line {}\nLine {}'.format(i, i+1), 0)

buffer.render()

buffer.listen()
curses.endwin()
