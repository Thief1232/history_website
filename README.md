# Firefox History Website

Веб-приложение на FastAPI, которое читает локальную историю Firefox и показывает самые посещаемые домены в виде диаграммы на странице.

## Что делает

- находит профиль Firefox в `~/.config/mozilla/firefox`
- копирует `places.sqlite` во временную директорию, чтобы безопасно читать базу истории
- читает URL из таблицы `moz_places`
- группирует посещения по доменам
- показывает топ посещаемых доменов на HTML-странице
- отдает те же данные в JSON-формате

## Структура

```text
history_website/
├── app.py
├── config.py
├── requirements.txt
├── routers/
│   ├── __init__.py
│   └── history.py
├── services/
│   ├── __init__.py
│   ├── charts.py
│   └── firefox_history.py
├── static/
│   └── styles.css
└── templates/
    └── index.html
```

## Установка

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Запуск

```bash
.venv/bin/fastapi dev app.py
```

После запуска откройте адрес, который покажет FastAPI. Обычно это `http://127.0.0.1:8000`.

## Страницы и API

- `/` - страница с диаграммой посещений
- `/api/history` - JSON с данными диаграммы

Можно изменить количество доменов через параметр `limit`:

```text
http://127.0.0.1:8000/?limit=15
http://127.0.0.1:8000/api/history?limit=15
```
