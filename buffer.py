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
        self.lncount = 0
        self.buffer = ''
        self.start = 0

    def moveup(self):
        self.start = max(self.start - 1, 0)

    def movedown(self):
        self.start = min(self.lncount - self.lines, self.start + 1)

    def addstr(self, s, attrs):
        s.replace('%[', '%%[')
        self.buffer += "%[{}]{}".format(attrs, s)

    def transform_buffer(self, s):
        result = ''
        lines = 0
        chars = 0
        attrs = {}
        i = 0
        while i < len(s):
            c = s[i]
            if c == '%' and s[i+1] == '[':
                esc = parse_escape(s, i + 2)
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
        return result, attrs

    def most_recent_attr(self, idx, attrs):
        if idx == 0:
            return attrs[idx] if idx in attrs else 0
        while idx not in attrs and idx > 0:
            idx -= 1
        return attrs[idx] if idx in attrs else 0

    def render(self):
        result, attrs = self.transform_buffer(self.buffer)
        self.lncount = result.count('\n') + 1
        self.win.clear()
        try:
            # FIXME when starting not at 0 find the nearest attr index < start_idx to apply
            # necessary attrs
            start_idx = self.get_start_idx(result, self.start)
            ats = self.most_recent_attr(start_idx, attrs)
            lines = 0
            for i in range(start_idx, len(result)):
                if i in attrs:
                    ats = attrs[i]
                if result[i] == '\n':
                    lines += 1
                if lines == self.lines:
                    break
                self.win.addstr(result[i], ats)
        except IndexError:
            pass

    def get_start_idx(self, s, line):
        try:
            idx = 0
            for i in range(line):
                idx = s.index('\n', idx) + 1  # pass the newline
            return idx
        except ValueError:
            return 0

    def listen(self):
        while True:
            c = s.getch()
            if c == ord("u"):
                b.moveup()
            if c == ord("d"):
                b.movedown()
            if c == ord('q') or c == 10:
                break
            self.render()


s = curses.initscr()
curses.noecho()
b = BufferedScreen(s, curses.LINES, curses.COLS)

for i in range(0, 500):
    b.addstr('line {}'.format(i), curses.A_STANDOUT if i %
             2 == 0 else curses.A_BOLD)

b.render()
b.listen()

curses.endwin()
