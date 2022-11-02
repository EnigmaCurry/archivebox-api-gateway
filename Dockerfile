FROM python:3.10

WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* /app/
RUN poetry install --no-root --no-dev

EXPOSE 8000
COPY . /app
CMD gunicorn archivebox_api.server:app --bind 0.0.0.0:8000 --worker-class aiohttp.GunicornWebWorker
