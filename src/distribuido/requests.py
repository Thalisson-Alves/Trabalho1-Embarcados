from time import sleep
from typing import Tuple

from distribuido.config import Config
from utils.interface import CentralRequestType
from distribuido.gpio_controller import GPIOController
from utils.server import request
from utils.try_log import try_log


def handle_requests(data: dict, addr: Tuple[str, int]) -> dict:
    # if data['type'] == ClientRequestType.UPDATE_STATE:
    #     response = {
    #         'success': True,
    #         'inputs': [{'name': x.name, 'value': 1}
    #                    for x in config.inputs],
    #         'outputs': [{'name': x.name, 'value': 1}
    #                    for x in config.outputs],
    #         'sensors': [{'name': x.name, 'value': 1}
    #                    for x in config.sensors]
    #     }
    #     return response
    # else:
    print('Unknown request!!')
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
            'sensors': controller.read_all_sensors(),
        }
        print('Enviando status pro Central')
        response = request(config.central_con.ip,
                           config.central_con.port, data)
        print(f'Response: {response}')

        sleep(1)
