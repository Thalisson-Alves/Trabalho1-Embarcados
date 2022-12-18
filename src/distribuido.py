import threading

from distribuido.config import Config
from distribuido.requests import update_client_states, handle_requests
from utils import server


def main():
    config = Config()

    threads = [
        threading.Thread(target=update_client_states, daemon=True),
    ]

    for t in threads:
        t.start()

    try:
        server.run(config.my_con.ip, config.my_con.port, handle_requests)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
