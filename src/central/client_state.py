
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union, overload

from utils.singleton import SingletonMeta

IS_CONFIGURED = False


@dataclass
class ConnectionInfo:
    ip: str
    port: int


@dataclass
class Device:
    name: str
    value: Union[int, float]


@dataclass
class ClientState:
    name: str
    conn_info: ConnectionInfo
    inputs: List[Device] = field(default_factory=list)
    outputs: List[Device] = field(default_factory=list)
    sensors: List[Device] = field(default_factory=list)


class ClientStates(metaclass=SingletonMeta):
    def __init__(self) -> None:
        with open(Path(__file__).parent / 'config.json', 'r') as f:
            config = json.load(f)

        self.clients = [
            ClientState(name=client.pop('name'),
                        conn_info=ConnectionInfo(**client))
            for client in config
        ]
        self._client_ips = {
            client.conn_info.ip: idx
            for idx, client in enumerate(self.clients)
        }

    @overload
    def __getitem__(self, idx: str) -> ClientState:...

    @overload
    def __getitem__(self, idx: int) -> ClientState:...

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.clients[idx]
        else:
            return self.clients[self._client_ips[idx]]

    def __len__(self) -> int:
        return len(self.clients)
