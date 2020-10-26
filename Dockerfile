FROM python:3.8-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt .
COPY dev_requirements.txt .

RUN apt-get update && \
    apt-get install -y netcat-openbsd gcc && \
    apt-get clean && \
    pip install -r dev_requirements.txt  && \
    apt purge -y gcc && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN python manage.py collectstatic --no-input

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
