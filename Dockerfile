# Alpine por que tem python 3.9: https://hub.docker.com/_/python
FROM python:3.9-rc-alpine

ENV PYTHONUNBUFFERED 1

RUN mkdir /code \
    apk update && \
    apk add --virtual build-deps gcc python-dev musl-dev && \
    apk add postgresql-dev && \
    apk add netcat-openbsd

WORKDIR /code

COPY requirements.txt /code/
COPY dev_requirements.txt /code/
RUN pip install -r dev_requirements.txt
COPY . /code/
