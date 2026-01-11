ARG PYTHON_VERSION=3.10-slim-bullseye

FROM python:${PYTHON_VERSION} AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN <<EOF
apt-get update
apt-get install -y --no-install-recommends curl iputils-ping traceroute
EOF

WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt
 
COPY ./src ./src

FROM base AS builder
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
