FROM python:3.12.0-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
  supervisor

RUN python -m pip install --upgrade pip
RUN pip install pipenv

WORKDIR /app

COPY ./supervisord.conf /etc/supervisor/conf.d/main.conf
COPY ./Pipfile /app/Pipfile

RUN pipenv install --deploy --ignore-pipfile --python /usr/local/bin/python3

COPY ./src /app

RUN chmod 744 docker-entrypoint.sh 

ENTRYPOINT ./docker-entrypoint.sh
