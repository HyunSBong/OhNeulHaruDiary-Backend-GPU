FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu20.04

ARG SPARK_VERSION=3.2.1
ARG HADOOP_VERSION=3.2
ARG PYTHON_VERSION=3.8.3

RUN apt-get -y update && apt-get -y upgrade && \
    apt-get -y install --no-install-recommends \
    wget tar bash curl vim \
    build-essential checkinstall \
    libreadline-gplv2-dev libncursesw5-dev libssl-dev \
    libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev liblzma-dev \
    openjdk-8-jdk \
    gcc+ \
    git

RUN wget https://mirror.navercorp.com/apache/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz

RUN tar -zxvf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /spark && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

RUN tar -xvf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations && \
    make install && \
    apt-get install -y python3-pip && \
    cd ..

ENV PYSPARK_PYTHON=python3

ENV LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:/usr/local/cuda/include:/usr/local/cuda/lib64

RUN pip3 install --upgrade pip && \
    pip3 install --upgrade setuptools