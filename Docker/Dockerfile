# syntax=docker/dockerfile:1

FROM python:3.9.9

WORKDIR bot/
COPY pip_packages.txt, main.py .

RUN pip3 install -r pip_packages.txt

CMD ["python3", "main.py"]

