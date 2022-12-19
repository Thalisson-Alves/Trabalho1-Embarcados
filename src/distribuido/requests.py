from time import sleep
from typing import Tuple

from distribuido.config import Config
from utils.interface import CentralRequestType, ClientRequestType
from distribuido.gpio_controller import GPIOController
from utils.server import request
from utils.try_log import try_log


def handle_requests(data: dict, addr: Tuple[str, int]) -> dict:
    print(f'Received {data}')
    controller = GPIOController()

    if data['type'] == ClientRequestType.SET_DEVICE:
        controller.set_device(data['name'], data['value'])
        response = {
            'success': True,
            'name': data['name'],
            'value': controller.read_output(data['name'])
        }
        print(f'Send response [{response}]')
        return response
    elif data['type'] == ClientRequestType.SET_ALARM_MODE:
        controller.alarm_mode = data['value']
        response = {
            'success': True,
            'value': controller.alarm_mode
        }
        print(f'Send response [{response}]')
        return response
    elif data['type'] == ClientRequestType.SET_ALL:
        for device in controller.outputs:
            controller.set_device(device, data['value'])
        response = {
            'success': True,
            'outputs': controller.read_all_outputs()
        }
        print(f'Send response [{response}]')
        return response
    elif data['type'] == ClientRequestType.CAN_SET_ALARM_MODE:
        response = {
            'success': True,
            'value': controller.can_set_alarm_mode()
        }
        print(f'Send response [{response}]')
        return response
    else:
        print(f"Unknown request: [{data}]")
        return {'success': False, 'detail': 'Unknown request'}


@try_log
def update_client_states():
    config = Config()
    controller = GPIOController()

    while True:
        data = {
            'type': CentralRequestType.UPDATE_STATE,
            'inputs': controller.read_all_inputs(),
            'outputs': controller.read_all_outputs(),
            'people': controller.people,
            'temperature': controller.read_temperature(),
            'humidity': controller.read_humidity(),
            'alarm_mode': controller.alarm_mode,
        }
        print('Enviando status pro Central')
        response = request(config.central_con.ip,
                           config.central_con.port, data)
        print(f'Response: {response}')

        sleep(1)


@try_log
def trigger_buzzer():
    config = Config()
    controller = GPIOController()

    while True:
        sleep(.1)
        if not controller.should_sound_buzzer():
            continue

        data = {
            'type': CentralRequestType.PROPAGATE,
            'propagation_data': {
                'type': ClientRequestType.SET_DEVICE,
                'name': 'Sirene do Alarme',
                'value': True,
            }
        }
        response = request(config.central_con.ip,
                           config.central_con.port, data)
        print(f'Propagate Response: {response}')
