FROM python:3.10

ENV PYTHONUNBUFFERED True

COPY . /opt/gcp-etl/
WORKDIR /opt/gcp-etl

RUN pip install --upgrade pip \
    pip install build \
    pip install --no-cache-dir -e .[develop]
