# builder image
FROM python:3.9-slim AS app_a_builder

RUN apt update && \
    apt install --no-install-recommends -y build-essential gcc && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --no-cache-dir --user -r requirements.txt


# runner image
FROM ubuntu:20.04 AS app_a_runner

RUN apt-get update && \
    apt-get install --no-install-recommends -y python3.9 python3-pip libpython3.9 python3-distutils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the uWSGI binary and all installed python packages
COPY --from=app_a_builder /root/.local/bin /usr/local/bin
COPY --from=app_a_builder /root/.local/lib/python3.9/site-packages /usr/local/lib/python3.9/dist-packages

RUN pip install --upgrade certifi

WORKDIR /
COPY . .

CMD ["uwsgi", "appA.ini"]

