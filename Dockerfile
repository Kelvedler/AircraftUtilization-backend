FROM python:3.12.0-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
  supervisor

RUN python -m pip install --upgrade pip

WORKDIR /app

COPY ./supervisord.conf /etc/supervisor/conf.d/main.conf
COPY ./requirements.txt /app/requirements.txt

RUN pip install -r ./requirements.txt

COPY ./src /app

RUN chmod 744 docker-entrypoint.sh 

ENTRYPOINT ./docker-entrypoint.sh
