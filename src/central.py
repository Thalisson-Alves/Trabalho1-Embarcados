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
    ]

    for t in threads:
        t.start()

    try:
        curses.wrapper(Screen().run)
    except Exception as e:
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
