import socket
import json
import time
import logging
from typing import NoReturn, Callable, Tuple

BUFFER_SIZE = 1024


def default_handler(data: dict, addr: Tuple[str, int]) -> dict:
    return {'success': True, 'data': data, 'addr': addr}


def run(host: str, port: int, handle_request: Callable[[dict, Tuple[str, int]], dict] = default_handler) -> NoReturn:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen()

        while True:
            conn, addr = sock.accept()
            with conn:
                data = conn.recv(BUFFER_SIZE)

                response = handle_request(json.loads(data), addr)
                if response:
                    conn.sendall(json.dumps(response).encode('utf-8'))


def request(host: str, port: int, data: dict) -> dict:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            sock.sendall(json.dumps(data).encode('utf-8'))
            return json.loads(sock.recv(1024))
    except Exception as e:
        return {'success': False, 'detail': str(e)}
