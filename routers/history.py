import sqlite3
from collections import Counter
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from config import TOP_SITES_LIMIT
from services.charts import build_chart_data, build_chart_rows
from services.firefox_history import get_history_counts


BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
router = APIRouter()


def safe_history_counts() -> Counter[str]:
    try:
        return get_history_counts()
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except sqlite3.Error as error:
        raise HTTPException(status_code=500, detail=f"Could not read Firefox history: {error}") from error


@router.get("/")
def index(request: Request, limit: int = Query(TOP_SITES_LIMIT, ge=1, le=50)):
    chart_data = build_chart_data(safe_history_counts(), limit)
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "chart_rows": build_chart_rows(chart_data),
            "limit": limit,
            "total_visits": sum(item["visits"] for item in chart_data),
        },
    )


@router.get("/api/history")
def history_api(limit: int = Query(TOP_SITES_LIMIT, ge=1, le=50)) -> JSONResponse:
    chart_data = build_chart_data(safe_history_counts(), limit)
    return JSONResponse({"limit": limit, "items": chart_data})
