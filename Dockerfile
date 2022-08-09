FROM python:3.8-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt .
COPY dev_requirements.txt .
# hadolint ignore=DL3008,DL3042,DL3027
RUN apt-get update && \
    apt-get install -y netcat-openbsd gcc && \
    apt-get clean && \
    pip install -r dev_requirements.txt  && \
    apt purge -y gcc && \
    apt autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN python manage.py collectstatic --no-input
