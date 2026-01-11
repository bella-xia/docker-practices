ARG PYTHON_VERSION=3.10-slim-bullseye

FROM python:${PYTHON_VERSION} AS base

# set python-related environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN <<EOF
apt-get update
apt-get install -y --no-install-recommends curl
EOF

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY ./app ./app

FROM base AS builder
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS dev-envs

RUN <<EOF
apt-get install -y --no-install-recommends vim
EOF

# used for development only: reloads after modification
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# TODO: needed if later requires access to git inside container
# apk add git

# TODO: needed if later requires access to docker inside container
# RUN <<EOF
# addgroup -S docker
# adduser -S --shell /bin/bash --ingroup docker
# EOF
# COPY --from=gloursdocker/docker / /
