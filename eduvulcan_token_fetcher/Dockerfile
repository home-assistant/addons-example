# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-debian
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV PYTHONUNBUFFERED=1

RUN \
  apt-get update \
  && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    ca-certificates \
  && python3 -m pip install --no-cache-dir --break-system-packages playwright \
  && python3 -m playwright install --with-deps chromium \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY rootfs /
COPY app /app
