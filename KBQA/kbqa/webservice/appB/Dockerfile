FROM python:3.9-alpine

WORKDIR /app

ADD . /app

RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers
RUN pip install -r requirements.txt
RUN apk del .tmp

CMD ["uwsgi", "appB.ini"]
