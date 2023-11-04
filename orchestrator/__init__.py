import logging
import os
import threading

import requests
from flask import Flask, jsonify, request

from deploy.config import LOG_LEVEL
from orchestrator.containers import reserve_free_container, free_container, Container

INSTANCE_ID = os.environ.get("INSTANCE_ID", "unknown")

logger = logging.getLogger(__name__)
app = Flask(__name__)
request_queue_lock = threading.Lock()
request_queue = []


@app.route("/")
def hello_world():
    return f"Orchestrator ID {INSTANCE_ID}"


@app.route("/health")
def health():
    return "OK"


@app.route("/new_request", methods=["POST"])
def new_request():
    incoming_request_data = request.data
    threading.Thread(
        target=process_request,
        args=(incoming_request_data,)
    ).start()
    return jsonify({"message": "Request received and processing started."})


def send_request_to_container(container_uuid: str, container: Container, incoming_request_data: bytes):
    logger.info(f"Sending request to container {container_uuid} with data {incoming_request_data}")
    container_ip = container["ip"]
    container_port = container["port"]
    requests.request(
        method="POST",
        url=f"http://{container_ip}:{container_port}",
        data=incoming_request_data,
    )
    logger.info(f"Received response from container {container_uuid}")


def process_request(incoming_request_data: bytes):
    reserved = reserve_free_container()
    if reserved:
        container_uuid, container = reserved
        send_request_to_container(container_uuid, container, incoming_request_data)
        logger.info(f"Request processed by container {container_uuid}")
        free_container(container_uuid)
        logger.info(f"Container {container_uuid} freed")
        with request_queue_lock:
            if len(request_queue) != 0:
                next_request = request_queue.pop(0)
                threading.Thread(
                    target=process_request,
                    args=(next_request,)
                ).start()
    else:
        with request_queue_lock:
            request_queue.append(incoming_request_data)
            logger.info(f"Request queued. Queue length: {len(request_queue)}")


if __name__ == "__main__":
    logging.basicConfig(level=LOG_LEVEL)
    app.run(port=80)
