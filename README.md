# MatterMost Search Bot
Бот для чата с открытым исходным кодом [MatterMost](https://docs.mattermost.com), предназначеный
для поиска информации в онлайн документации (wiki/readthedocs/microimpuls/apidoc/jsdoc).
Бот написан на Python c использованием библиотеки [mmpy_bot](https://mmpy-bot.readthedocs.io/en/latest/).
Настройки бота хранятся в файле config.json.
Пример конфигурации находится в файле [config.example.json](https://github.com/Damiryh/mm-search-bot/blob/master/config.example.json)

Подготовка:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Запуск бота:
```bash
source .venv/bin/activate
python main.py
```

## Примеры поисковых запросов
```
global EXPR     # Сквозной поиск
history         # Поиск по истории сообщений

wiki EXPR
micro EXPR
gitdev EXPR
history EXPR
```

EXPR - регулярное выражение

## Сборка и запуск Docker образа:
```bash
docker image build --tag mm-search-bot .
docker run -p 80:80 -p 8080:8080 -p 443:443 mm-search-bot
```
