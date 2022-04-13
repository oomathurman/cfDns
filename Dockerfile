FROM python:alpine

ADD ./scripts /scripts

ENV timer "*/5 * * * *"

ENTRYPOINT /bin/sh -c "echo '$timer python /scripts/cfDns.py | crontab - && crond -fd8"