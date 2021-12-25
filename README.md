# Google Sheets Monitoring Bot

## Запуск бота

Для запуска бота нужен токен телеграм-бота и API Key для Google Sheets:
[получение API Key для проекта в Google Cloud](https://developers.google.com/workspace/guides/create-credentials#api-key),
[включение Google Sheets API в проекте Google Cloud](https://developers.google.com/workspace/guides/enable-apis)

Пример запуска бота:

    python3 ./bot/main.py $TELEGRAM_TOKEN $GOOGLE_SHEETS_API_KEY /path/to/the/database

При запуске docker-контейнера для передачи токена и ключа используются переменные окружения,
файл базы данных монтируется по пути ``/database``.

Пример запуска контейнера (*из корня репозитория*):

    docker build -f ./Docker/Dockerfile --tag tg-bot .

    docker run -e TELEGRAM_TOKEN={your telegram token} \
        -e SHEETS_API_KEY={your google sheets api key} \
        -v /path/to/the/database:/database \
        tg-bot
