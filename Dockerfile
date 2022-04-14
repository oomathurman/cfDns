FROM python:alpine

ADD ./scripts /scripts

ENV timer "*/5 * * * *"

RUN pip install requests &> /dev/null
RUN pip install colorama &> /dev/null

ENTRYPOINT /bin/sh -c "echo '$timer python /scripts/cfDns.py' | crontab - && crond -fd8"