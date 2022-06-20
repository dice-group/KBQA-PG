# builder image
FROM python:3.9-slim AS app_b_builder

RUN apt update && \
    apt install --no-install-recommends -y build-essential gcc locales && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*



COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --no-cache-dir --user -r requirements.txt



# runner image
FROM ubuntu:20.04 AS app_b_runner

RUN apt-get update && \
    apt-get install --no-install-recommends -y python3.9 python3-pip libpython3.9 locales && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8 
ENV LANGUAGE en_US:en 
ENV LC_ALL en_US.UTF-8



# Copy the uWSGI binary and all installed python packages
COPY --from=app_b_builder /root/.local/bin /usr/local/bin
COPY --from=app_b_builder /root/.local/lib/python3.9/site-packages /usr/local/lib/python3.9/dist-packages

RUN pip install --upgrade certifi
RUN python3.9 -c "import nltk; nltk.download('wordnet')"
RUN python3.9 -m spacy download en_core_web_sm

WORKDIR /
COPY . .

CMD ["uwsgi", "appB.ini"]
