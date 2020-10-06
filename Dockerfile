FROM python:3.8-alpine
# set work directory
WORKDIR /usr/src/app
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev openssl
# install dependencies
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
# copy project
COPY . .

