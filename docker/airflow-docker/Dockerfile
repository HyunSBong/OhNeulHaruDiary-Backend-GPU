FROM docker.io/bitnami/airflow:2-debian-10

ENV DEBIAN_FRONTEND noninteractive

USER root

RUN apt-get update && \
    apt-get install -y software-properties-common gnupg2 && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EB9B1D8886F44E2A && \
    add-apt-repository "deb http://security.debian.org/debian-security stretch/updates main" && \ 
    apt-get update && \
    apt-get install -y openjdk-8-jdk

ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64
RUN export JAVA_HOME

COPY . /
RUN pip install apache-airflow-providers-apache-spark celery wheel psycopg2-binary
