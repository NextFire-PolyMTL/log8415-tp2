import logging
import sys
from multiprocessing import Pool

from bench.scenario import my_test

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")

    try:
        nb = int(sys.argv[1])
    except IndexError:
        raise ValueError("You must provide the number of parallel requests to send")

    try:
        rounds = int(sys.argv[2])
    except IndexError:
        rounds = 1

    logger.info(f"Sending {nb} requests in parallel, {rounds} times")
    with Pool(processes=nb) as p:
        for _ in range(rounds):
            p.map(my_test, range(nb))
