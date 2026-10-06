FROM node:22-slim AS frontend-builder

WORKDIR /app/src/apps/theme/static_src

COPY src/apps/theme/static_src/package.json src/apps/theme/static_src/package-lock.json ./
RUN npm ci

WORKDIR /app
COPY . .

WORKDIR /app/src/apps/theme/static_src
RUN npm run build

FROM python:3.14-slim AS builder

ARG POETRY_VERSION=2.4.1

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_REQUESTS_TIMEOUT=120 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

RUN python -m venv "${VIRTUAL_ENV}" && \
    /usr/local/bin/python -m pip install --no-cache-dir "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock ./
RUN poetry sync --only main --no-root --no-ansi

FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/src:/app" \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"

RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

COPY --chown=appuser:appuser . .
COPY --from=frontend-builder --chown=appuser:appuser \
    /app/src/apps/theme/static/css/dist/ \
    /app/src/apps/theme/static/css/dist/

WORKDIR /app/src

USER appuser

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
