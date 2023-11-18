import logging

import requests

from orchestrator.utils import get_orchestator_ip

logger = logging.getLogger(__name__)


def my_test(request_num: int):
    logger.info("Starting senario")

    url_orchestrator = f"http://{get_orchestator_ip()}"

    resp = requests.request(
        method="POST",
        url=f"{url_orchestrator}/new_request",
        data=b"Request number " + str(request_num).encode(),
    )
    resp.raise_for_status()
    logger.info(f"Received response from orchestrator: {resp.json()}")
