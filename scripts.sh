#!/bin/sh -xe

### Prerequisites (Linux/macOS) ###
# - Python 3.11
# - Poetry (https://python-poetry.org/docs/#installation)
# - Docker (https://docs.docker.com/get-docker/)
# - AWS credentials configured in ~/.aws/credentials

# Setup the virtual environment with all dependencies (including dev ones)
poetry install

# Bootstrap the AWS infrastructure and deploy the application
poetry run python3 -m deploy

# Run benchmarks
# > Build the Docker image
docker build -t bench -f .docker/bench.Dockerfile .
# > Start the benchmark
# >> Mounts:
# >> - AWS credentials in read-only mode
# >> - Results directory
docker run --rm -it -v $HOME/.aws:/root/.aws:ro  -v $PWD/results:/src/results bench

# Cleanup all AWS resources at the end
poetry run python3 -m deploy.cleanup

# Results
echo "Open the results/ directory to see the benchmark results."
