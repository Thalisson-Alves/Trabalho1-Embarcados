
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, overload

from utils.singleton import SingletonMeta

IS_CONFIGURED = False


@dataclass
class ConnectionInfo:
    ip: str
    port: int


@dataclass
class Device:
    name: str
    value: Optional[bool]


@dataclass
class ClientState:
    name: str
    conn_info: ConnectionInfo
    inputs: List[Device] = field(default_factory=list)
    outputs: List[Device] = field(default_factory=list)
    people: Optional[int] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    alarm_mode: Optional[bool] = None

    def find_output_by_name(self, name: str) -> Device:
        for device in self.outputs:
            if device.name == name:
                return device
        raise RuntimeError('Output not found')


class ClientStates(metaclass=SingletonMeta):
    def __init__(self) -> None:
        with open(Path(__file__).parent / 'config.json', 'r') as f:
            config = json.load(f)

        self.clients = [
            ClientState(
                name=client.pop('name'),
                conn_info=ConnectionInfo(**client),
                inputs=sorted([
                    Device(device_name, None)
                    for device_name in config['inputs']
                ], key=lambda x: x.name),
                outputs=sorted([
                    Device(device_name, None)
                    for device_name in config['outputs']
                ], key=lambda x: x.name),
            )
            for client in config['rooms']
        ]
        self._client_ips = {
            client.conn_info.ip: idx
            for idx, client in enumerate(self.clients)
        }

    @overload
    def __getitem__(self, idx: str) -> ClientState: ...

    @overload
    def __getitem__(self, idx: int) -> ClientState: ...

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.clients[idx]
        else:
            return self.clients[self._client_ips[idx]]

    def __len__(self) -> int:
        return len(self.clients)

    def __iter__(self):
        return iter(self.clients)
