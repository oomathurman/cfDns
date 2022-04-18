FROM python:alpine

ADD ./scripts /scripts

RUN pip install requests &> /dev/null

ENTRYPOINT /bin/sh -c "echo '$cronTime python /scripts/cfDns.py' | crontab - && crond -f"