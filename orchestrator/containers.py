import json
import threading
import uuid

from typing import TypedDict, Optional

CONTAINERS_FILENAME = "containers.json"
STATUS_FREE = "free"
STATUS_BUSY = "busy"

file_lock = threading.Lock()


class Container(TypedDict):
    ip: str
    port: str
    status: str


def _write_containers_to_file(containers: dict[str, Container]) -> None:
    with open(CONTAINERS_FILENAME, "w") as f:
        json.dump(containers, f)


def _read_containers_from_file() -> dict[str, Container]:
    try:
        with open(CONTAINERS_FILENAME, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def register_new_container(ip: str, port: str) -> None:
    container_uuid = str(uuid.uuid4())
    container = {
        "ip": ip,
        "port": port,
        "status": STATUS_FREE,
    }

    with file_lock:
        containers = _read_containers_from_file()
        containers[container_uuid] = container
        _write_containers_to_file(containers)


def reserve_free_container() -> Optional[tuple[str, Container]]:
    with file_lock:
        containers = _read_containers_from_file()
        for container_uuid, container in containers.items():
            if container["status"] == STATUS_FREE:
                containers[container_uuid]["status"] = STATUS_BUSY
                _write_containers_to_file(containers)
                return container_uuid, container
    return None


def free_container(container_uuid: str) -> None:
    with file_lock:
        containers = _read_containers_from_file()
        containers[container_uuid]["status"] = STATUS_FREE
        _write_containers_to_file(containers)
