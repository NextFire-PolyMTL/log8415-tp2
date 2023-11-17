#!/bin/sh -xe

### Prerequisites (Linux/macOS) ###
# - Python 3.11
# - Poetry (https://python-poetry.org/docs/#installation)
# - AWS credentials configured in ~/.aws/credentials

# Setup the virtual environment with all dependencies (including dev ones)
poetry install

# Bootstrap the AWS infrastructure and deploy the application
poetry run python3 -m deploy

# Cleanup all AWS resources at the end
poetry run python3 -m deploy.cleanup

# Run the tests
poetry run python3 -m tests
