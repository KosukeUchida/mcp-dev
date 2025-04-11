FROM mcr.microsoft.com/vscode/devcontainers/python:3.12-bookworm

# 必要なソフトのインストール
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# uvのインストール
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

RUN pip install uv

# Default command
CMD ["/bin/bash"]