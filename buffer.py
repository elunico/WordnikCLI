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
        # self.start -= 1
        self.start = max(self.start - 1, 0)

    def movedown(self):
        # self.start += 1
        self.start = min(self.lncount - self.lines, self.start + 1)

    def addstr(self, s, attrs=0):
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
                elif chars == self.cols:
                    lines += 1
                    chars = 0
                    result += '\x07'
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
            start_idx = self.get_start_idx(result, self.start)
            ats = self.most_recent_attr(start_idx, attrs)
            lines = 0
            for i in range(start_idx, len(result)):
                if i in attrs:
                    ats = attrs[i]
                # inserted in the string to represent wrapping at the end of a line
                # different from \n because no \n is inserted by a new line is still
                # started and coutns towards the line count
                if result[i] == '\x07':
                    lines += 1
                    continue
                if result[i] == '\n':
                    lines += 1
                if lines == self.lines:
                    break
                self.win.addstr(result[i], ats)
            self.win.refresh()
        except IndexError:
            pass

    def get_start_idx(self, s, line):
        try:
            idx = 0
            for i in range(line):
                # \n represents explicit new lines and
                # \x07 represents wrapping at self.cols
                # so when we seek a new line we have to see the nearest (min)
                # index of the two
                idx = min(better_index_of(s, '\n', idx), better_index_of(
                    s, '\x07', idx)) + 1  # pass the newline
            return idx
        except ValueError:
            return 0

    def listen(self):
        while True:
            c = self.win.getch()
            if c == ord("u"):
                b.moveup()
            if c == ord("d"):
                b.movedown()
            if c == ord('q') or c == 10:
                break
            self.render()


def better_index_of(string, substring, start=0):
    try:
        return string.index(substring, start)
    except ValueError:
        return 2 ** 64


if __name__ == '__main__':
    s = curses.initscr()
    curses.noecho()
    b = BufferedScreen(s, curses.LINES, curses.COLS)

    for i in range(0, 500):
        b.addstr('line {}'.format(i), curses.A_STANDOUT if i %
                 2 == 0 else curses.A_BOLD)

    b.render()
    b.listen()

    curses.endwin()
