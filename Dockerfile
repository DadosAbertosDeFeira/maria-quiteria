FROM python:3.8-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt .
COPY dev_requirements.txt .

# we can remove git if no pip package is installed from git
RUN apt-get update && \
    apt-get install -y netcat-openbsd gcc git && \
    apt-get clean && \
    pip install -r dev_requirements.txt  && \
    apt purge -y gcc git && \
    apt autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN python manage.py collectstatic --no-input
