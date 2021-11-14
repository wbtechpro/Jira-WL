FROM python:3.8 as before_etrypoint

ENV PYTHONUNBUFFERED 1

RUN apt -y update && \
    apt install -y postgresql-client python3-dev cron

RUN pip install -U pip uwsgi

WORKDIR /usr/src/api/

COPY ./requirements.txt /usr/src/api/
RUN pip install -r /usr/src/api/requirements.txt

COPY ./ /usr/src/api/


# Cron 
COPY ./cron-command /etc/cron.d/cron-command

RUN chmod 0644 /etc/cron.d/cron-command

RUN crontab /etc/cron.d/cron-command

FROM before_etrypoint as without_entrypoint

FROM before_etrypoint as with_entrypoint
ENTRYPOINT ["/usr/src/api/scripts/docker-entrypoint.sh"]

