FROM pytorch/pytorch:latest

ENV POETRY_VIRTUALENVS_IN_PROJECT=1

WORKDIR /src

COPY pyproject.toml poetry.lock ./
RUN pip3 install poetry && \
    poetry self add poetry-plugin-export && \
    poetry export --only worker -o requirements.txt && \
    pip3 install -r requirements.txt && \
    rm -rf ~/.cache/

COPY worker worker

ENTRYPOINT [ "python3" ]
CMD [ "-m", "worker" ]
EXPOSE 8000
