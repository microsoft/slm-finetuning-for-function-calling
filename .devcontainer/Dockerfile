FROM python:3.11-slim-bullseye AS base

RUN set -x

RUN apt-get update \
    && apt-get -y install curl \
    && apt-get -y install net-tools \
    && apt-get -y install procps \
    && apt-get -y install build-essential \
    && apt-get -y install docker.io

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN pip install ipython ipykernel

RUN set +x

CMD bash