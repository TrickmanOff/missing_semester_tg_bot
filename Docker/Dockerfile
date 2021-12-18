# syntax=docker/dockerfile:1

FROM python:3.9.9

WORKDIR /bot
COPY /Docker/pip_packages.txt main.py config.ini ./

RUN pip3 install --no-cache-dir -r pip_packages.txt

ENTRYPOINT ["python3", "main.py", "config.ini"]

