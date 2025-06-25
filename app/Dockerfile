FROM python:3.10-slim

WORKDIR /app

RUN pip install poetry && \
    apt-get update && \
    apt-get install -y libaio1 unzip

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-root

COPY . .

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]