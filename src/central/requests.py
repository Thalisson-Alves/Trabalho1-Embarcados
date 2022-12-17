from typing import Tuple
from utils.server import request
from central.client_state import ClientStates, Device
from utils.interface import CentralRequestType


def handle_requests(data: dict, addr: Tuple[str, int]) -> dict:
    client_states = ClientStates()
    if data['type'] == CentralRequestType.UPDATE_STATE:
        client = client_states[addr[0]]
        client.inputs = [
            Device(name, value)
            for name, value in data['inputs'].items()
        ]
        client.outputs = [
            Device(name, value)
            for name, value in data['outputs'].items()
        ]
        client.sensors = [
            Device(name, value)
            for name, value in data['sensors'].items()
            if value is not None
        ]
        # print('-' * 50)
        # print(client)
        # print('-' * 50)
        return {'success': True, 'detail': 'Data updated'}
    else:
        print('Unknown request!!')
        return {'success': False, 'detail': 'Unknown request'}
