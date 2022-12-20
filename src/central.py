import curses
import json
import logging
import pathlib
import threading

from central.requests import handle_requests
from central.screen import Screen
from utils import server


def main():
    with open(pathlib.Path(__file__).parent/'central'/'config.json') as f:
        config = json.load(f)

    logging.basicConfig(filename=config['log_file'], encoding='utf-8', level=logging.INFO, format='%(asctime)s,%(message)s', datefmt='%d/%m/%Y %I:%M:%S')

    threads = [
        threading.Thread(target=server.run, args=(
            config['ip'], config['port'], handle_requests), daemon=True),
    ]

    for t in threads:
        t.start()

    try:
        curses.wrapper(Screen().run)
    except (SystemExit, KeyboardInterrupt):
        ...
    except:
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
