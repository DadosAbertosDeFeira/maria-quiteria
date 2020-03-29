FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
COPY dev_requirements.txt /code/
RUN pip install -r dev_requirements.txt
COPY . /code/