# MatterMost Search Bot
Бот для чата с открытым исходным кодом [MatterMost](https://docs.mattermost.com), предназначеный
для поиска информации в онлайн документации (wiki/readthedocs/microimpuls/apidoc/jsdoc).
Бот написан на Python c использованием библиотеки [mmpy_bot](https://mmpy-bot.readthedocs.io/en/latest/).
Настройки бота хранятся в файле config.json.

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
rtd EXPR
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
