FROM python:3.13-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.7.6 /uv /uvx /usr/local/bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONPATH=.

COPY . /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

CMD [ "uv", "run", "-m", "src.main" ]