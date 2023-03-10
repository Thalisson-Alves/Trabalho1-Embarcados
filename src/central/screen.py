import curses
import io
import logging
from curses.textpad import rectangle
from typing import Tuple

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
    def __init__(self) -> None:
        self.last_events = io.StringIO()
        ch = logging.StreamHandler(self.last_events)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(
            logging.Formatter('%(levelname)s|%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S')
        )
        self.log = logging.getLogger('screen')
        self.log.addHandler(ch)

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
        curses.curs_set(0)
        self.room_selected = self.option_selected = 0

        self.initialize_boxes()

        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)

    def initialize_boxes(self):
        h, w = self.size

        self.temperature_box = Box(self.stdscr, (4, w // 5 - 2),
                                   (3, 1), 'Temperatura')
        self.humidity_box = Box(self.stdscr, (4, w // 5 - 2),
                                (3, 1 + w // 5), 'Umidade')
        self.people_box = Box(self.stdscr, (4, w // 5 - 2),
                              (3, 1 + 2 * w // 5), 'N??mero de Pessoas')
        self.total_people_box = Box(self.stdscr, (4, w // 5 - 2),
                              (3, 1 + 3 * w // 5), 'N??mero de Pessoas Total')
        self.alarm_box = Box(self.stdscr, (4, w // 5 - 2),
                             (3, 1 + 4 * w // 5), 'Modo Alarme')

        self.menu_box = Box(self.stdscr, (7, w // 2 - 2), (8, 1), 'Menu')

        self.options = [
            'Acionar dispositivo',
            'Acionar todos os dispositivos',
            'Desligar todos os dispositivos',
            'Acionar sistema de alarme',
            'Acionar alarme de inc??ndio',
            'Sair',
        ]

        self.trigger_alarm_box = Box(self.stdscr, (7, w // 2 - 2), (8, 1 + w // 2), '??ltimos eventos')

        self.inputs_box = Box(self.stdscr, (h - 21, w // 2 - 2),
                              (16, 1), 'Dispositivos de Entrada')
        self.outputs_box = Box(self.stdscr, (h - 21, w // 2 - 2),
                               (16, w // 2 + 1), 'Dispositivos de Sa??da')

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
        elif user_input == curses.KEY_RESIZE:
            self.initialize_boxes()

    def apply_action(self):
        if self.option_selected == 0:
            self.option_selected = len(self.options)
        elif self.option_selected == 1:
            value = True
            response = request(self.client.conn_info.ip, self.client.conn_info.port,
                        {'type': ClientRequestType.SET_ALL,
                        'value': value})
            if response['success']:
                for device in self.client.outputs:
                    device.value = value

                logging.info('Acionamento de todos os dispositivos da %s para %s', self.client.name, format_value(value))
                self.log.info('%s %s %s', self.client.name, 'Aciona tudo', format_value(value))
            else:
                logging.error('Tentativa de acionar todos os dispositivos da %s para %s', self.client.name, format_value(value))
                self.log.error('%s %s %s', self.client.name, 'Aciona tudo', format_value(value))
        elif self.option_selected == 2:
            value = False
            response = request(self.client.conn_info.ip, self.client.conn_info.port,
                        {'type': ClientRequestType.SET_ALL,
                        'value': value})
            if response['success']:
                for device in self.client.outputs:
                    device.value = value

                logging.info('Acionamento de todos os dispositivos da %s para %s', self.client.name, format_value(value))
                self.log.info('%s %s %s', self.client.name, 'Aciona tudo', format_value(value))
            else:
                logging.error('Tentativa de acionar todos os dispositivos da %s para %s', self.client.name, format_value(value))
                self.log.error('%s %s %s', self.client.name, 'Aciona tudo', format_value(value))
        elif self.option_selected == 3:
            value = not self.client.alarm_mode
            if value:
                for client in self.clients:
                    response = request(client.conn_info.ip, client.conn_info.port,
                                    {'type': ClientRequestType.CAN_SET_ALARM_MODE})
                    if not response.get('value', True):
                        logging.error('N??o ?? poss??vel acionar Sistema de Alarme nesse momento da %s para %s', client.name, format_value(value))
                        self.log.error('%s %s', self.client.name, 'N??o ?? poss??vel acionar Sistema de Alarme nesse momento')
                        return

            for client in self.clients:
                response = request(client.conn_info.ip, client.conn_info.port,
                                {'type': ClientRequestType.SET_ALARM_MODE,
                                'value': value})
                if response['success']:
                    client.alarm_mode = response['value']
                    logging.info('Configura????o do Sistema de Alarme da %s para %s', client.name, format_value(client.alarm_mode))
                    self.log.info('%s %s %s', client.name, 'Sistema de Alarme', format_value(client.alarm_mode))
                else:
                    logging.info('Erro ao tentar configurar o Sistema de Alarme da %s para %s', client.name, format_value(value))
                    self.log.error('%s %s %s', client.name, 'Sistema de Alarme', format_value(value))
        elif self.option_selected == 4:
            buzzer_name = 'Sirene do Alarme'
            for client in self.clients:
                device = client.find_output_by_name(buzzer_name)
                response = request(client.conn_info.ip, client.conn_info.port,
                                {'type': ClientRequestType.SET_DEVICE,
                                'name': device.name,
                                'value': not device.value})
                if response['success']:
                    device.value = response['value']
                    logging.info('Configura????o do %s da %s para %s', device.name, client.name, format_value(device.value))
                    self.log.info('%s %s %s', client.name, device.name, format_value(device.value))
                else:
                    logging.error('Erro ao tentar configurar %s da %s para %s', device.name, client.name, format_value(not device.value))
                    self.log.error('%s %s %s', client.name, device.name, format_value(not device.value))
        elif self.option_selected == 5:
            logging.info('Saindo do sistema')
            exit(0)
        else:
            device = self.client.outputs[self.option_selected - len(self.options)]
            response = request(self.client.conn_info.ip, self.client.conn_info.port,
                        {'type': ClientRequestType.SET_DEVICE,
                        'name': device.name,
                        'value': not device.value})
            if response['success']:
                device.value = response['value']
                logging.info('Configura????o do %s para %s', device.name, format_value(device.value))
                self.log.info('%s %s %s', self.client.name, device.name, format_value(device.value))
            else:
                logging.error('Erro ao tentar configurar %s para %s', device.name, format_value(not device.value))
                self.log.error('%s %s %s', self.client.name, device.name, format_value(not device.value))

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

    def render_last_events(self):
        events = self.last_events.getvalue().splitlines()[-1:-5:-1]
        for i, msg in enumerate(events, 2):
            if not msg: continue
            t, s = msg.split('|', 1)
            at = curses.color_pair(2) if 'error' == t.lower() else curses.color_pair(4)
            self.stdscr.attron(at)
            self.trigger_alarm_box.write(i, 2, s, center=True)
            self.stdscr.attroff(at)

        self.last_events.seek(0)
        self.last_events.truncate(0)
        self.last_events.write('\n'.join(events[::-1]) + '\n')

    def render_menu(self):
        for i, option in enumerate(self.options, 1):
            if i - 1 == self.option_selected:
                self.menu_box.write(i, 2, '>')
                self.stdscr.attron(curses.color_pair(3))

            option = f'{i}. {option}'
            self.menu_box.write(i, 4, option.ljust(self.menu_box.w - 5))

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
