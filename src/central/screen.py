import curses
from curses.textpad import rectangle
from typing import Tuple

from central.client_state import ClientStates
from utils.singleton import SingletonMeta

MAX_COLUMN_WIDTH = 45


class Screen(metaclass=SingletonMeta):
    def run(self, stdscr: 'curses._CursesWindow'):
        self.initialize(stdscr)
        while True:
            self.events()
            self.update()
            self.render()

    def events(self):
        ...

    def update(self):
        ...

    def render(self):
        self.stdscr.erase()

        for func_name in filter(lambda x: x.startswith('render_'), dir(self)):
            getattr(self, func_name)()

        self.stdscr.refresh()

    def render_title(self):
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.attron(curses.A_BOLD)

        title = 'Servidor Central'
        _, cx = self.centered_pos(title)
        self.stdscr.addstr(1, cx, title)

        self.stdscr.attroff(curses.color_pair(1))
        self.stdscr.attroff(curses.A_BOLD)

    def render_client_state(self):
        clients = ClientStates()

        start_y = 10
        start_x = 3
        self.stdscr.addstr(start_y, start_x, 'Entradas')
        for i, x in enumerate(clients[self.cursor_x].inputs, 1):
            self.stdscr.addstr(i + start_y, start_x, x.name.ljust(MAX_COLUMN_WIDTH, '.') + str(x.value))

    def initialize(self, stdscr: 'curses._CursesWindow'):
        self.cursor_x = self.cursor_y = 0
        self.stdscr = stdscr

        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    @property
    def size(self) -> Tuple[int, int]:
        return self.stdscr.getmaxyx()

    def centered_pos(self, s: str) -> Tuple[int, int]:
        h, w = self.size
        return (h // 2), (w // 2) - (len(s) // 2) - (len(s) & 1)


'''

            # Initialization
            stdscr.erase()
            height, width = stdscr.getmaxyx()

            if k == curses.KEY_DOWN:
                self.cursor_y = self.cursor_y + 1
            elif k == curses.KEY_UP:
                self.cursor_y = self.cursor_y - 1
            elif k == curses.KEY_RIGHT:
                self.cursor_x = self.cursor_x + 1
            elif k == curses.KEY_LEFT:
                self.cursor_x = self.cursor_x - 1

            self.cursor_x = max(0, self.cursor_x)
            self.cursor_x = min(width-1, self.cursor_x)

            self.cursor_y = max(0, self.cursor_y)
            self.cursor_y = min(height-1, self.cursor_y)

            # Declaration of strings
            title = "Curses example"[:width-1]
            subtitle = "Written by Clay McLeod"[:width-1]
            keystr = "Last key pressed: {}".format(k)[:width-1]
            statusbarstr = "Press 'q' to exit | STATUS BAR | Pos: {}, {}".format(
                self.cursor_x, self.cursor_y)
            if k == 0:
                keystr = "No key press detected..."[:width-1]

            # Centering calculations
            start_x_title = int(
                (width // 2) - (len(title) // 2) - len(title) % 2)
            start_x_subtitle = int(
                (width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
            start_x_keystr = int(
                (width // 2) - (len(keystr) // 2) - len(keystr) % 2)
            start_y = int((height // 2) - 2)

            # Rendering some text
            whstr = "Width: {}, Height: {}".format(width, height)
            stdscr.addstr(0, 0, whstr, curses.color_pair(1))

            # Render status bar
            stdscr.attron(curses.color_pair(3))
            stdscr.addstr(height-1, 0, statusbarstr)
            stdscr.addstr(height-1, len(statusbarstr), " " *
                          (width - len(statusbarstr) - 1))
            stdscr.attroff(curses.color_pair(3))

            # Turning on attributes for title
            stdscr.attron(curses.color_pair(2))
            stdscr.attron(curses.A_BOLD)

            # Rendering title
            stdscr.addstr(start_y, start_x_title, title)

            # Turning off attributes for title
            stdscr.attroff(curses.color_pair(2))
            stdscr.attroff(curses.A_BOLD)

            # Print rest of text
            stdscr.addstr(start_y + 1, start_x_subtitle, subtitle)
            stdscr.addstr(start_y + 3, (width // 2) - 2, '-' * 4)
            stdscr.addstr(start_y + 5, start_x_keystr, keystr)
            stdscr.move(self.cursor_y, self.cursor_x)

            # Refresh the screen
            stdscr.refresh()

            # Wait for next input
            k = stdscr.getch()

'''
