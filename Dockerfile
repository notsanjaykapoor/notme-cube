FROM python:3.12.3-slim as runner

ENV PYTHONUNBUFFERED=1

RUN apt-get -y update && \
    apt-get install -y busybox curl dnsutils gcc gettext libffi-dev libpq-dev netcat-traditional tmux && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync

FROM runner as base
ARG APP_VERSION=version
WORKDIR /app
ADD . ./
