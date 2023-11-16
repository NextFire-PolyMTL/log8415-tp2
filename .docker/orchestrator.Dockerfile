FROM python:3.11-slim

ENV POETRY_VIRTUALENVS_IN_PROJECT=1

WORKDIR /src

COPY pyproject.toml poetry.lock ./
RUN pip3 install poetry && \
    poetry install --only orchestrator --no-root && \
    rm -rf ~/.cache/

COPY orchestrator orchestrator
COPY containers.json .

ENTRYPOINT [ "poetry", "run", "python3" ]
CMD [ "-m", "orchestrator" ]

EXPOSE 8000
