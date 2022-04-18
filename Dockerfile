FROM python:alpine

LABEL org.opencontainers.image.source https://github.com/oomathurman/cfdns

ADD ./scripts /scripts

RUN pip install requests &> /dev/null

ENTRYPOINT /bin/sh -c "echo '$cronTime python /scripts/cfDns.py' | crontab - && crond -f"