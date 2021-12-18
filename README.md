# Simple Bot

Токен передаётся как аргумент при запуске контейнера.

Пример запуска контейнера (*из корня репозитория*):

    docker build -f ./Docker/Dockerfile --tag tg-bot .
    docker run tg-bot $(cat ~/token)

