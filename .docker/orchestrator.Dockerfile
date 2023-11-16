FROM python:3.11-slim

WORKDIR /src

RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --only orchestrator

COPY orchestrator app

ENTRYPOINT [ "poetry", "run", "gunicorn", "-b", "0.0.0.0", "app:app" ]
EXPOSE 8000
