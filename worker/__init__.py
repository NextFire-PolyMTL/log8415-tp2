import os

from flask import Flask

INSTANCE_ID = os.environ.get("INSTANCE_ID", "unknown")

app = Flask(__name__)


@app.route("/")
def hello_world():
    return f"Worker ID {INSTANCE_ID}"


@app.route("/health")
def health():
    return "OK"
