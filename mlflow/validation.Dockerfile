FROM amd64/python:3.9-slim

RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*
 
RUN pip install -U pip &&\
    pip install boto3==1.35.95 mlflow==2.21.2 psycopg2-binary

RUN cd /tmp && \
    wget https://dl.min.io/client/mc/release/linux-amd64/mc && \
    chmod +x mc && \
    mv mc /usr/bin/mc