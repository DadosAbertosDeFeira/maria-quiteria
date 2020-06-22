FROM python:3.8-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY . /code/

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y netcat-openbsd gcc && \
    apt-get clean && \
    pip install -r dev_requirements.txt && \
    python manage.py collectstatic --no-input

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
