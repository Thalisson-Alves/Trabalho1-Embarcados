from typing import Tuple

from central.client_state import ClientStates, Device
from utils.interface import CentralRequestType
from utils.server import request


def handle_requests(data: dict, addr: Tuple[str, int]) -> dict:
    client_states = ClientStates()
    if data['type'] == CentralRequestType.UPDATE_STATE:
        client = client_states[addr[0]]
        client.inputs = sorted([
            Device(name, value)
            for name, value in data['inputs'].items()
        ], key=lambda x: x.name)
        client.outputs = sorted([
            Device(name, value)
            for name, value in data['outputs'].items()
        ], key=lambda x: x.name)
        for field in ('people', 'temperature', 'humidity', 'alarm_mode'):
            if data[field] is not None:
                setattr(client, field, data[field])
        return {'success': True, 'detail': 'Data updated'}
    if data['type'] == CentralRequestType.PROPAGATE:
        fails = 0
        for client in client_states:
            response = request(client.conn_info.ip, client.conn_info.port,
                               data['propagation_data'])
            if not response['success']: fails += 1
        return {'success': fails < len(client_states), 'detail': f'Propagated with {fails} fails'}
    else:
        return {'success': False, 'detail': 'Unknown request'}
