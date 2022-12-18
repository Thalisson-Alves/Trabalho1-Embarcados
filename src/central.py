import curses
import os
import threading

from central.requests import handle_requests
from central.screen import Screen
from utils import server

HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', '10921'))


def main():
    # TODO: Change all prints to log
    threads = [
        threading.Thread(target=server.run, args=(
            HOST, PORT, handle_requests), daemon=True),
        threading.Thread(target=curses.wrapper, args=(
            Screen().run, ), daemon=True),
    ]

    for t in threads:
        t.start()


if __name__ == '__main__':
    main()
