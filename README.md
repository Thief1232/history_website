# Browser History Website

FastAPI app for viewing local browser history as simple domain charts.

![Browser History preview](preview.png)

## Features

- Finds installed browser profiles on Linux
- Supports Firefox, Chrome, Chromium, Brave, Edge, Opera, and Vivaldi
- Reads history from a temporary SQLite copy, not the live database
- Groups HTTP/HTTPS visits by domain
- Shows installed browsers only
- Displays data as bar or pie chart
- Exposes the same data as JSON

## Install

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run

```bash
.venv/bin/fastapi dev main.py
```

Open the URL printed by FastAPI, usually:

```text
http://127.0.0.1:8000
```

## Usage

- Use the slider to choose how many domains to show.
- Pick an installed browser from the browser list.
- Pick `Bar` or `Pie` chart.
- Use `JSON` link for raw data.

## API

```text
http://127.0.0.1:8000/api/history?limit=15&chart_type=pie&browser=chrome
```

Parameters:

- `limit`: number of top domains, from `1` to `50`
- `chart_type`: `bar` or `pie`
- `browser`: browser key, for example `firefox`, `chrome`, `brave`
