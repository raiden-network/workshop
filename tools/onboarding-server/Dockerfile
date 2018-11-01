FROM python:3.6
LABEL maintainer="Ulrich Petri <ulrich@brainbot.com>"

ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD onboarding_server.py /onboarding_server.py

ENTRYPOINT ["python3", "/onboarding_server.py"]
