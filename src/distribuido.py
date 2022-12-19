import threading

from distribuido.config import Config
from distribuido import requests
from utils import server


def main():
    config = Config()

    threads = [
        threading.Thread(target=requests.update_client_states, daemon=True),
        threading.Thread(target=requests.trigger_buzzer, daemon=True),
    ]

    for t in threads:
        t.start()

    try:
        server.run(config.my_con.ip, config.my_con.port, requests.handle_requests)
    except:
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
