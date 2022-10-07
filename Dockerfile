# pull official base image
# FROM python:3.9.5-slim-buster
FROM nginx/unit:1.22.0-python3.9

# custom label for the docker image
LABEL version="0.1" maintainer="mikro_mongo_app"

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app/

# copy unit config
COPY config.json /docker-entrypoint.d/config.json
