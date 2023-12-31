import logging
import os
import threading
from queue import SimpleQueue

import requests
from flask import Flask, jsonify, request

from orchestrator.containers import Container, free_container, reserve_free_container

INSTANCE_ID = os.environ.get("INSTANCE_ID", "unknown")

logger = logging.getLogger(__name__)

app = Flask(__name__)

request_queue: SimpleQueue[bytes] = SimpleQueue()


@app.route("/")
def hello_world():
    return f"Orchestrator ID {INSTANCE_ID}"


@app.route("/health")
def health():
    return "OK"


@app.route("/new_request", methods=["POST"])
def new_request():
    incoming_request_data = request.data
    threading.Thread(target=process_request, args=(incoming_request_data,)).start()
    return jsonify({"message": "Request received and processing started."})


def send_request_to_container(
    container_uuid: str, container: Container, incoming_request_data: bytes
):
    logger.info(
        f"Sending request to container {container_uuid} "
        f"with data {incoming_request_data}"
    )
    container_ip = container["ip"]
    container_port = container["port"]
    resp = requests.request(
        method="POST",
        url=f"http://{container_ip}:{container_port}/run_model",
        data=incoming_request_data,
    )
    resp.raise_for_status()
    logger.info(f"Received response from container {container_uuid}: {resp.json()}")


def process_request(incoming_request_data: bytes):
    reserved = reserve_free_container()
    if reserved:
        container_uuid, container = reserved
        try:
            send_request_to_container(container_uuid, container, incoming_request_data)
        except requests.HTTPError as e:
            logger.exception(e)
        finally:
            free_container(container_uuid)
            logger.info(f"Container {container_uuid} freed")
        if not request_queue.empty():
            next_request = request_queue.get_nowait()
            threading.Thread(target=process_request, args=(next_request,)).start()
    else:
        request_queue.put(incoming_request_data)
        logger.info(f"Request queued. Queue length: {request_queue.qsize()}")