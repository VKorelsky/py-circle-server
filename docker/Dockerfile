FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.5.21 /uv /uvx /bin/

COPY server.py ./app/
COPY uv.lock ./app/
COPY pyproject.toml ./app/

WORKDIR /app
RUN uv sync --locked

CMD ["uv", "run", "server.py"]