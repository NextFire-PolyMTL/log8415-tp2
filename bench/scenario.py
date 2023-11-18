import requests

from orchestrator.utils import get_orchestator_ip


def my_test(request_num: int):
    url_orchestrator = f"http://{get_orchestator_ip()}"
    resp = requests.request(
        method="POST",
        url=f"{url_orchestrator}/new_request",
        data=b"Request number " + str(request_num).encode(),
    )
    resp.raise_for_status()
    print(f"[{request_num=}] Received response from orchestrator: {resp.json()}")
