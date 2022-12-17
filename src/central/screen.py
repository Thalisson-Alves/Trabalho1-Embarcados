import curses
from curses.textpad import rectangle
from typing import List, Tuple

from central.client_state import ClientState, ClientStates, Device
from utils.singleton import SingletonMeta

MAX_COLUMN_WIDTH = 45


class Box:
    def __init__(self, win: 'curses._CursesWindow', size: Tuple[int, int], pos: Tuple[int, int], title: str = '') -> None:
        self.win = win
        self.h, self.w = size
        self.y, self.x = pos
        self.title = title and title.center(len(title) + 4)

    def render(self):
        rectangle(self.win, self.y, self.x, self.y + self.h, self.x + self.w)
        if self.title:
            self.win.addstr(self.y, self.x +
                            centered_x(self.title, self.w), self.title)

    def write(self, y: int, x: int, s: str) -> None:
        self.win.addstr(self.y + y, self.x + x, s)


class Screen(metaclass=SingletonMeta):
    def run(self, stdscr: 'curses._CursesWindow'):
        self.initialize(stdscr)
        while True:
            self.events()
            self.update()
            self.render()

    def initialize(self, stdscr: 'curses._CursesWindow'):
        self.clients = ClientStates()

        self.stdscr = stdscr
        self.cursor_x = self.cursor_y = 0

        self.initialize_boxes()

        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def initialize_boxes(self):
        h, w = self.size

        self.rooms_boxes = [
            Box(self.stdscr, (1, w // len(self.clients) - 1),
                (0, 1 + i * w // len(self.clients)), x.name)
            for i, x in enumerate(self.clients)
        ]

        self.temperature_box = Box(self.stdscr, (5, w // 4 - 2),
                                   (3, 1), 'Temperatura')
        self.humidity_box = Box(self.stdscr, (5, w // 4 - 2),
                                (3, 1 + w // 4), 'Umidade')
        self.people_box = Box(self.stdscr, (5, w // 4 - 2),
                              (3, 1 + 2 * w // 4), 'Número de Pessoas')
        self.alarm_box = Box(self.stdscr, (5, w // 4 - 2),
                             (3, 1 + 3 * w // 4), 'Modo Alarme')

        self.inputs_box = Box(self.stdscr, (h - 21, w // 2 - 2),
                              (20, 1), 'Dispositivos de Entrada')
        self.outputs_box = Box(self.stdscr, (h - 21, w // 2 - 2),
                               (20, w // 2 + 1), 'Dispositivos de Saída')

        self.boxes = [
            *self.rooms_boxes,
            self.temperature_box,
            self.humidity_box,
            self.people_box,
            self.alarm_box,
            self.inputs_box,
            self.outputs_box,
        ]

    def events(self):
        ...

    def update(self):
        ...

    def render(self):
        self.stdscr.erase()

        for func_name in filter(lambda x: x.startswith('render_'), dir(self)):
            getattr(self, func_name)()

        for box in self.boxes:
            box.render()

        self.stdscr.refresh()

    def render_title(self):
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.attron(curses.A_BOLD)

        title = 'Servidor Central'
        cx = centered_x(title, self.size[1])
        self.stdscr.addstr(1, cx, title)

        self.stdscr.attroff(curses.color_pair(1))
        self.stdscr.attroff(curses.A_BOLD)

    def render_client_state(self):
        self._render_devices(self.client.inputs, self.inputs_box)
        self._render_devices(self.client.outputs, self.outputs_box)

    @staticmethod
    def _render_devices(devices: List[Device], box: Box):
        for i, x in enumerate(devices, 2):
            v = '???' if x.value is None else ['OFF', 'ON '][x.value]
            box.write(i, 2, x.name.ljust(box.w - len(v) - 3, '.') + v)

    @property
    def size(self) -> Tuple[int, int]:
        return self.stdscr.getmaxyx()

    @property
    def client(self) -> ClientState:
        return self.clients[self.cursor_x]


def centered_x(s: str, w: int) -> int:
    return w // 2 - len(s) // 2
