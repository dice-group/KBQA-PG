FROM python:3.9-slim

WORKDIR /app

ADD . /app

RUN pip install --upgrade pip
RUN apt update && \
    apt install -y openjdk-11-jre && \
    apt clean && \
    apt install --no-install-recommends -y build-essential gcc && \
    apt clean && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt

CMD ["uwsgi", "appA.ini"]
