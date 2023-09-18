# log8415-tp1

**Prerequisites:** [Python 3.11](https://www.python.org), [Poetry](https://python-poetry.org/) and [Docker](https://www.docker.com/). AWS credentials must be configured in `~/.aws/credentials`.

To setup the venv and install all dependencies:

```sh
poetry install
```

## Web application

```sh
poetry install --only app
poetry run gunicorn app:app
```

Or with Docker:

```sh
docker build -t app -f .docker/app.Dockerfile .
docker run --rm -it -p 8000:8000 app
```

## Deployment

```sh
poetry install --only deploy
poetry run python3 -m deploy
```

To terminate all resources:

```sh
poetry run python3 -m deploy.cleanup
```

## Benchmarking

```sh
poetry install --only bench
poetry run python3 -m bench
```

Or with Docker:

```sh
docker build -t bench -f .docker/bench.Dockerfile .
docker run --rm -it -v $HOME/.aws:/root/.aws:ro  -v $PWD/results:/src/results bench
```
