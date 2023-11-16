FROM python:3.11-slim

WORKDIR /src

RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --only orchestrator

COPY orchestrator orchestrator

ENTRYPOINT [ "poetry", "run", "gunicorn", "-b", "0.0.0.0", "orchestrator:app" ]
EXPOSE 8000
