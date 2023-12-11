FROM ghcr.io/osgeo/gdal:alpine-small-latest

LABEL MAINTAINER=sparber@ubique.ch

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN apt-get -y update
RUN apt-get install -y --fix-missing python3-pip
RUN apt-get clean

COPY . /opt/app
WORKDIR /opt/app

RUN pip install -r requirements.txt
