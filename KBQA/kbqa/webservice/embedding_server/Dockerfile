FROM python:3.9-alpine

WORKDIR .

COPY . .

RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers
RUN pip install -r requirements.txt
RUN apk del .tmp

CMD ["uwsgi", "embedding_server.ini"]
