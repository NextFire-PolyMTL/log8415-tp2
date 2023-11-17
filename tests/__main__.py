import logging
from multiprocessing import Pool
import scenario

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logging.basicConfig(level="INFO")
    with Pool(5) as p:
        p.map(scenario.my_test, range(5))
