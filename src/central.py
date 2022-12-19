import curses
import os
import threading
import logging

from central.requests import handle_requests
from central.screen import Screen
from utils import server

HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', '10921'))
LOG_FILE = os.getenv('LOG_FILE', '/tmp/central-log.csv')


def main():
    logging.basicConfig(filename=LOG_FILE, encoding='utf-8', level=logging.INFO, format='%(asctime)s,%(message)s', datefmt='%d/%m/%Y %I:%M:%S')
    screen = Screen()
    handler = logging.StreamHandler(screen.last_events)
    handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(handler)

    threads = [
        threading.Thread(target=server.run, args=(
            HOST, PORT, handle_requests), daemon=True),
    ]

    for t in threads:
        t.start()

    try:
        curses.wrapper(screen.run)
    except:
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
