import logging
from datetime import datetime

from bench.analysis import analyze
from bench.config import (
    CLUSTER_1_PATH,
    CLUSTER_1_TARGET_NAME,
    CLUSTER_2_PATH,
    CLUSTER_2_TARGET_NAME,
    LB_NAME,
    LOG_LEVEL,
)
from bench.scenarios import run_scenarios
from bench.utils import get_lb_arn_dns, get_tg_arn, wait_lb

logger = logging.getLogger(__name__)


def main():
    wait_lb(LB_NAME)
    lb_arn, lb_dns = get_lb_arn_dns(LB_NAME)
    logger.info(f"{(lb_arn, lb_dns)=}")

    # Run scenarios
    start_time = datetime.utcnow()
    for cluster in (CLUSTER_1_PATH, CLUSTER_2_PATH):
        run_scenarios(lb_dns, cluster)
    end_time = datetime.utcnow()

    # Analyze metrics
    logger.info('Starting analysis')
    tg1_arn = get_tg_arn(CLUSTER_1_TARGET_NAME)
    tg2_arn = get_tg_arn(CLUSTER_2_TARGET_NAME)
    logger.info(f"{(tg1_arn, tg2_arn)=}")
    for tg_arn in (tg1_arn, tg2_arn, None):
        analyze(lb_arn, start_time, end_time, tg_arn=tg_arn)

    logger.info('Done. Please check the contents of the `./results` directory.')


if __name__ == '__main__':
    logging.basicConfig(level=LOG_LEVEL)
    main()
