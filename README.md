# Google Sheets Monitoring Bot

Автор:
<font color=pink>Егоров</font>
<font color=orange>Егор</font>
<font color=purple>Александрович</font> [@TrickmanOff](https://t.me/TrickmanOff)

## Что делает бот

Бот [@googlesheets_monitoring_bot](https://t.me/googlesheets_monitoring_bot)
мониторит публичные Google Sheets таблицы и сообщает, если в указанном
диапазоне ячеек изменилось значение (может быть удобно, например, для отслеживания
таблиц с оценками)

## Где сейчас запущен

Запущен на сервере [DigitalOcean](https://www.digitalocean.com/products/droplets/).

При создании тега/релизе в *main* собирается Docker-образ и пушится в Docker Hub,
откуда скачивается на сервер и затем запускается с помощью WatchTower.

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

## Что используется

| Что               | Зачем                                  |
|-------------------|----------------------------------------|
| PeeWee (ORM)      | Для хранения *notifiers* пользователей |
| Google Sheets API | Для чтения таблиц                      |


## TODO
- логирование
- бэкап базы данных куда-то (на сервер?)
