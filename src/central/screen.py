import curses
from curses.textpad import rectangle
from typing import List, Tuple

from central.client_state import ClientState, ClientStates
from utils.interface import ClientRequestType
from utils.server import request
from utils.singleton import SingletonMeta


class Box:
    def __init__(self, win: 'curses._CursesWindow', size: Tuple[int, int], pos: Tuple[int, int], title: str = '') -> None:
        self.win = win
        self.h, self.w = size
        self.y, self.x = pos
        self.title = title and title.center(len(title) + 4)
        self.title_attr = []

    def render(self):
        rectangle(self.win, self.y, self.x, self.y + self.h, self.x + self.w)
        if not self.title:
            return

        for at in self.title_attr:
            self.win.attron(at)

        self.win.addstr(self.y, self.x +
                        centered_x(self.title, self.w), self.title)

        for at in self.title_attr:
            self.win.attroff(at)

    def write(self, y: int, x: int, s: str, *, center: bool = False) -> None:
        if center:
            x = centered_x(s, self.w)
        self.win.addstr(self.y + y, self.x + x, s)


class Screen(metaclass=SingletonMeta):
    def run(self, stdscr: 'curses._CursesWindow'):
        self.initialize(stdscr)
        while True:
            self.update()
            self.render()

            curses.napms(10)

    def initialize(self, stdscr: 'curses._CursesWindow'):
        self.clients = ClientStates()

        self.stdscr = stdscr
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)
        self.room_selected = self.option_selected = 0
        self.last_errors: List[str] = []

        self.initialize_boxes()

        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def initialize_boxes(self):
        h, w = self.size

        self.temperature_box = Box(self.stdscr, (4, w // 5 - 2),
                                   (3, 1), 'Temperatura')
        self.humidity_box = Box(self.stdscr, (4, w // 5 - 2),
                                (3, 1 + w // 5), 'Umidade')
        self.people_box = Box(self.stdscr, (4, w // 5 - 2),
                              (3, 1 + 2 * w // 5), 'Número de Pessoas')
        self.total_people_box = Box(self.stdscr, (4, w // 5 - 2),
                              (3, 1 + 3 * w // 5), 'Número de Pessoas Total')
        self.alarm_box = Box(self.stdscr, (4, w // 5 - 2),
                             (3, 1 + 4 * w // 5), 'Modo Alarme')

        self.menu_box = Box(self.stdscr, (7, w // 2 - 2), (8, 1), 'Menu')

        self.options = [
            'Acionar dispositivo',
            'Acionar sistema de alarme',
            'Acionar alarme de incêndio',
            'Sair',
        ]

        self.trigger_alarm_box = Box(self.stdscr, (7, w // 2 - 2), (8, 1 + w // 2), 'Alarmes disparados')

        self.inputs_box = Box(self.stdscr, (h - 21, w // 2 - 2),
                              (16, 1), 'Dispositivos de Entrada')
        self.outputs_box = Box(self.stdscr, (h - 21, w // 2 - 2),
                               (16, w // 2 + 1), 'Dispositivos de Saída')

        self.boxes = [
            self.temperature_box,
            self.humidity_box,
            self.people_box,
            self.total_people_box,
            self.alarm_box,
            self.menu_box,
            self.trigger_alarm_box,
            self.inputs_box,
            self.outputs_box,
        ]

    def update(self):
        user_input = self.stdscr.getch()
        if user_input in (curses.KEY_DOWN, ord('j')):
            if self.option_selected < len(self.options):
                self.option_selected = (self.option_selected + 1) % len(self.options)
            else:
                self.option_selected = len(self.options) + (self.option_selected - len(self.options) + 1) % len(self.client.outputs)
        elif user_input in (curses.KEY_UP, ord('k')):
            if self.option_selected < len(self.options):
                self.option_selected = (self.option_selected - 1) % len(self.options)
            else:
                self.option_selected = len(self.options) + (self.option_selected - len(self.options) - 1) % len(self.client.outputs)
        elif user_input == curses.KEY_BACKSPACE:
            self.option_selected = 0
        elif user_input == 10:  # Enter
            self.apply_action()
        elif user_input == ord('\t'):
            self.room_selected = (self.room_selected + 1) % len(self.clients)
        elif user_input == curses.KEY_BTAB:
            self.room_selected = (self.room_selected - 1) % len(self.clients)
        else:
            ... #self.trigger_alarm_box.write(4, 4, f'Typed: [{user_input}]')

    def apply_action(self):
        if self.option_selected == 0:
            self.option_selected = len(self.options)
        elif self.option_selected == 1:
            for client in self.clients:
                response = request(client.conn_info.ip, client.conn_info.port,
                                {'type': ClientRequestType.SET_ALARM_MODE,
                                'value': not client.alarm_mode})
                if response['success']:
                    client.alarm_mode = response['value']
                else:
                    # self.last_errors.append(f'Erro ao acionar Sistema de Alarme da {client.name}')
                    self.last_errors.append(str(response))
        elif self.option_selected == 2:
            buzzer_name = 'Sirene do Alarme'
            for client in self.clients:
                device = client.find_output_by_name(buzzer_name)
                response = request(client.conn_info.ip, client.conn_info.port,
                                {'type': ClientRequestType.SET_DEVICE,
                                'name': device.name,
                                'value': not device.value})
                if response['success']:
                    device.value = response['value']
                else:
                    # self.last_errors.append(f'Erro ao acionar Sistema de Alarme da {client.name}')
                    self.last_errors.append(str(response))
        elif self.option_selected == 3:...
        else:
            device = self.client.outputs[self.option_selected - len(self.options)]
            response = request(self.client.conn_info.ip, self.client.conn_info.port,
                        {'type': ClientRequestType.SET_DEVICE,
                        'name': device.name,
                        'value': not device.value})
            if response['success']:
                device.value = response['value']
            else:
                # self.last_errors.append(f'Erro ao acionar {device.name} da {self.client.name}')
                self.last_errors.append(str(response))

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

        title = self.client.name
        cx = centered_x(title, self.size[1])
        self.stdscr.addstr(1, cx, title)

        self.stdscr.attroff(curses.color_pair(1))
        self.stdscr.attroff(curses.A_BOLD)

    def render_client_state(self):
        self._render_input_devices()
        self._render_output_devices()

        self.temperature_box.write(2, 2, format_value(
            self.client.temperature), center=True)
        self.humidity_box.write(2, 2, format_value(
            self.client.humidity), center=True)
        self.people_box.write(2, 2, format_value(
            self.client.people), center=True)
        self.total_people_box.write(2, 2, format_value(sum(x.people or 0 for x in self.clients)), center=True)
        self.alarm_box.write(2, 2, format_value(self.client.alarm_mode), center=True)

    def render_error_messages(self):
        self.last_errors[:] = self.last_errors[-4:]
        self.stdscr.attron(curses.color_pair(2))
        for i, msg in enumerate(self.last_errors, 2):
            self.trigger_alarm_box.write(i, 2, msg, center=True)
        self.stdscr.attroff(curses.color_pair(2))

    def render_menu(self):
        for i, option in enumerate(self.options, 1):
            if i - 1 == self.option_selected:
                self.menu_box.write(i + 1, 2, '>')
                self.stdscr.attron(curses.color_pair(3))

            option = f'{i}. {option}'
            self.menu_box.write(i + 1, 4, option.ljust(self.menu_box.w - 5))

            if i - 1 == self.option_selected:
                self.stdscr.attroff(curses.color_pair(3))

    def _render_output_devices(self):
        for i, x in enumerate(self.client.outputs, 2):
            if i - 2 == self.option_selected - len(self.options):
                self.outputs_box.write(i, 2, '>')
                self.stdscr.attron(curses.color_pair(3))

            v = format_value(x.value)
            self.outputs_box.write(i, 4, x.name.ljust(self.outputs_box.w - len(v) - 5, '.') + v)

            if i - 2 == self.option_selected - len(self.options):
                self.stdscr.attroff(curses.color_pair(3))

    def _render_input_devices(self):
        for i, x in enumerate(self.client.inputs, 2):
            v = format_value(x.value)
            self.inputs_box.write(i, 4, x.name.ljust(self.inputs_box.w - len(v) - 5, '.') + v)

    @property
    def size(self) -> Tuple[int, int]:
        return self.stdscr.getmaxyx()

    @property
    def client(self) -> ClientState:
        return self.clients[self.room_selected]


def centered_x(s: str, w: int) -> int:
    return w // 2 - len(s) // 2


def format_value(value) -> str:
    if value is None:
        return '???'
    if isinstance(value, bool):
        return ('OFF', 'ON')[value]
    if isinstance(value, float):
        return f'{value:.2f}'
    return str(value)
