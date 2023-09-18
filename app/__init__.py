import os

from flask import Flask

INSTANCE_ID = os.environ.get("INSTANCE_ID", "unknown")
ROUTE_RULE = os.environ.get("ROUTE_RULE", "/")

app = Flask(__name__)


@app.route(ROUTE_RULE)
def hello_world():
    return f"Instance ID {INSTANCE_ID} is responding now!"


@app.route("/health")
def health():
    return "OK"
