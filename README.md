# log8415-tp2

**Prerequisites:** [Python 3.10 or 3.11](https://www.python.org), [Poetry](https://python-poetry.org/) and [Docker](https://www.docker.com/). AWS credentials must be configured in `~/.aws/credentials`.

## Deployment

```sh
poetry install --with deploy,bench
poetry run python3 -m deploy
poetry run python3 -m bench
```

To terminate all resources:

```sh
poetry run python3 -m deploy.cleanup
```
