import socket
import json
from typing import NoReturn, Callable, Tuple

BUFFER_SIZE = 1024


def default_handler(data: dict, addr: Tuple[str, int]) -> dict:
    print(f'Handling {addr}')
    print(data)

    return {'success': True, 'data': data}


def run(host: str, port: int, handle_request: Callable[[dict, Tuple[str, int]], dict] = default_handler) -> NoReturn:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, port))
        sock.listen()

        while True:
            conn, addr = sock.accept()
            with conn:
                print(f'Connected by {addr}')
                data = conn.recv(BUFFER_SIZE)
                print(f'Received {data}')

                response = handle_request(json.loads(data), addr)
                if response:
                    conn.sendall(json.dumps(response).encode('utf-8'))
                    print(f'Sent {response}')


def request(host: str, port: int, data: dict) -> dict:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.sendall(json.dumps(data).encode('utf-8'))
        return json.loads(sock.recv(1024))
