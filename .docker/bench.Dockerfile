FROM python:3.11-slim

WORKDIR /src

RUN pip install --upgrade pip setuptools poetry~=1.6.0
COPY pyproject.toml poetry.lock ./
RUN poetry install --only bench

COPY bench bench

ENTRYPOINT [ "poetry", "run", "python3", "-m", "bench" ]
