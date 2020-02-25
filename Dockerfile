FROM python:3.7-alpine

RUN apk update && apk upgrade
RUN apk add build-base

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY src/ /src
WORKDIR /src

CMD exec gunicorn --bind 0.0.0.0:$PORT app:app
