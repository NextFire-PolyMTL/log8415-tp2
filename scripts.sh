#!/bin/sh -xe

### Prerequisites (Linux/macOS) ###
# - Python 3.11
# - Poetry (https://python-poetry.org/docs/#installation)
# - AWS credentials configured in ~/.aws/credentials

# Setup the virtual environment for deploy and bench
poetry install --with deploy,bench

# Bootstrap the AWS infrastructure and deploy the application
poetry run python3 -m deploy

# Run the bench
poetry run python3 -m bench 5 4     # 5 parallel requests, 4 times

# Cleanup all AWS resources at the end
poetry run python3 -m deploy.cleanup
