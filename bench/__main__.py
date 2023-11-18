import logging
from multiprocessing import Pool

from bench.scenario import my_test

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    with Pool(processes=5) as p:
        p.map(my_test, range(5))
