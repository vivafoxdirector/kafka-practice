FROM python:3.7.5-slim
USER root

RUN apt-get update
RUN apt-get -y install locales && localedef -f UTF-8 -i ko_KR ko_KR.UTF-8

ENV LANG ko_KR.UTF-8
ENV LANGUAGE ko_KR:ko
ENV LC_ALL ko_KR.UTF-8
ENV TERM xterm

COPY requirements.txt .
#WORKDIR /app/opt

RUN apt-get install -y vim less
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
#RUN ls -la /app/opt
RUN pip install -r requirements.txt