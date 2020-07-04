FROM python:3.8-slim as dev

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt .
COPY dev_requirements.txt .

RUN apt-get update && \
    apt-get install -y netcat-openbsd gcc && \
    apt-get clean && \
    pip install -r dev_requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM dev as artifact

RUN python manage.py collectstatic --no-input
