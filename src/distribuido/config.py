import json
from dataclasses import dataclass
from pathlib import Path

from utils.singleton import SingletonMeta


@dataclass
class GPIOItem:
    name: str
    pin: int


@dataclass
class ConnectionInfo:
    ip: str
    port: int


class Config(metaclass=SingletonMeta):
    def __init__(self) -> None:
        with open(Path(__file__).parent / 'config.json', 'r') as f:
            data = json.load(f)

        self.name: str = data['nome']
        self.central_con = ConnectionInfo(
            data['ip_servidor_central'],
            data['porta_servidor_central'])
        self.my_con = ConnectionInfo(
            data['ip_servidor_distribuido'],
            data['porta_servidor_distribuido'])
        self.inputs = [GPIOItem(x['tag'], x['gpio'])
                       for x in data['inputs']]
        self.outputs = [GPIOItem(x['tag'], x['gpio'])
                        for x in data['outputs']]
        self.sensors = [GPIOItem(x['tag'], x['gpio'])
                        for x in data['sensor_temperatura']]
