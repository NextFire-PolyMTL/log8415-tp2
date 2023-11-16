import logging

from orchestrator import INSTANCE_ID, app

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    logger.info(f"Starting orchestrator {INSTANCE_ID} on port 8000")
    app.run(host="0.0.0.0", port=8000)
