# Simple Bot

Токен передаётся как аргумент при запуске контейнера.

Для запуска бота нужен токен телеграм-бота и API Key для Google Sheets: [получение API Key для проекта в Google Cloud](https://developers.google.com/workspace/guides/create-credentials#api-key), [включение Google Sheets API](https://developers.google.com/workspace/guides/enable-apis)

Пример запуска бота:

    python3 main.py $TELEGRAM_TOKEN $GOOGLE_SHEETS_API_KEY

Пример запуска контейнера (*из корня репозитория*):

    docker build -f ./Docker/Dockerfile --tag tg-bot .
    docker run tg-bot $(cat ~/token)

