import threading

from distribuido.config import Config
from distribuido.requests import update_client_states
from utils import server


def main():
    config = Config()

    threads = [
        threading.Thread(target=server.run, args=(config.my_con.ip, config.my_con.port)),
        threading.Thread(target=update_client_states),
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()


if __name__ == '__main__':
    main()
