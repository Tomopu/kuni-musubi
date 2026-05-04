FROM mcr.microsoft.com/devcontainers/typescript-node:1-22-bookworm

RUN apt-get update \
  && export DEBIAN_FRONTEND=noninteractive \
  && apt-get install -y --no-install-recommends \
    bubblewrap \
    ca-certificates \
    curl \
    git \
    jq \
    pipx \
    postgresql-client \
    python3 \
    python3-pip \
    python3-venv \
    ripgrep \
    socat \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/node/.claude \
  && chown -R node:node /home/node/.claude

COPY .devcontainer/managed-settings.json /etc/claude-code/managed-settings.json
