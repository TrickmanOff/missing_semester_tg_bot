# syntax=docker/dockerfile:1

FROM python:3.9.9

WORKDIR /bot
COPY /Docker/pip_packages.txt /bot ./

RUN pip3 install --no-cache-dir -r pip_packages.txt

CMD ["sh", "-c", "python3 /bot/main.py ${TELEGRAM_TOKEN} ${SHEETS_API_KEY} /database"]
# CMD "python3" "/bot/main.py" $TELEGRAM_TOKEN $SHEETS_API_KEY "/database"

