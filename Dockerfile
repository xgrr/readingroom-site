FROM python:3.7

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src
COPY requirements.txt ./
RUN useradd --create-home --shell /bin/bash django
RUN chown django -R /usr/src
USER django
RUN python -m venv env && . env/bin/activate && pip install --no-cache-dir -r requirements.txt
COPY . /usr/src
EXPOSE 8000
CMD ["env/bin/uwsgi", "app/config/http-server.ini"]

