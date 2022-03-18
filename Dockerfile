FROM python:3.10

WORKDIR /app

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* /app/
RUN poetry install --no-root --no-dev

EXPOSE 8000

COPY . /app
CMD gunicorn archivebox_api.server:app --worker-class aiohttp.GunicornWebWorker
