FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    netcat-openbsd \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]