import logging
from threading import Barrier, Thread
from time import sleep

import requests

logger = logging.getLogger(__name__)

barrier = Barrier(2)


def run_scenarios(lb_dns: str, path: str):
    barrier.reset()
    thread1 = Thread(target=scenario1, args=(lb_dns, path))
    thread2 = Thread(target=scenario2, args=(lb_dns, path))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()


def scenario1(lb_dns: str, path: str):
    logger.info(f"Starting scenario 1 on {path}")
    barrier.wait()
    for _ in range(1000):
        _make_req(lb_dns, path)
    logger.info(f"Finished scenario 1 on {path}")


def scenario2(lb_dns: str, path: str):
    logger.info(f"Starting scenario 2 on {path}")
    barrier.wait()
    for _ in range(500):
        _make_req(lb_dns, path)
    sleep(60)
    for _ in range(1000):
        _make_req(lb_dns, path)
    logger.info(f"Finished scenario 2 on {path}")


def _make_req(lb_dns, path):
    requests.get(f"http://{lb_dns}{path}")
