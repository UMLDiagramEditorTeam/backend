FROM python:3.13-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/

FROM base AS deps

COPY pyproject.toml uv.lock ./

RUN uv sync \
    --frozen \
    --no-dev

FROM base AS runtime

RUN useradd -m -u 10001 appuser

COPY --from=deps /app/.venv /app/.venv

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

USER appuser

EXPOSE 8000

CMD [ "gunicorn", "app.main:app", "-c", "gunicorn_config.py" ]
