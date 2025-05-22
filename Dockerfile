FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.5.21 /uv /uvx /bin/

COPY server.py .
CMD ["uv", "run", "server.py"]

