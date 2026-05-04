import sqlite3
from collections import Counter
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from config import TOP_SITES_LIMIT
from services.browser_history import BROWSER_LABELS, available_browsers, get_history_counts, normalize_browser
from services.charts import CHART_LABELS, build_chart_data, build_chart_model, normalize_chart_type


BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
router = APIRouter()


def detect_browser_from_user_agent(user_agent: str) -> str:
    user_agent = user_agent.lower()

    if "edg/" in user_agent:
        return "edge"
    if "opr/" in user_agent or "opera" in user_agent:
        return "opera"
    if "vivaldi" in user_agent:
        return "vivaldi"
    if "firefox" in user_agent:
        return "firefox"
    if "chromium" in user_agent:
        return "chromium"
    if "chrome" in user_agent or "crios" in user_agent:
        return "chrome"
    return "firefox"


def resolve_browser(request: Request, browser: str | None, browser_labels: dict[str, str]) -> str:
    if browser_labels and browser in browser_labels:
        return browser

    if browser_labels:
        detected = detect_browser_from_user_agent(request.headers.get("user-agent", ""))
        if detected in browser_labels:
            return detected

        return next(iter(browser_labels))

    if browser:
        return normalize_browser(browser)

    return detect_browser_from_user_agent(request.headers.get("user-agent", ""))


def safe_history_counts(browser: str) -> Counter[str]:
    try:
        return get_history_counts(browser)
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail={
                "message": str(error),
                "browser": browser,
                "browser_label": BROWSER_LABELS.get(browser, "выбранный браузер"),
            },
        ) from error
    except sqlite3.Error as error:
        browser_label = BROWSER_LABELS.get(browser, "selected browser")
        raise HTTPException(status_code=500, detail=f"Could not read {browser_label} history: {error}") from error


@router.get("/")
def index(
    request: Request,
    limit: int = Query(TOP_SITES_LIMIT, ge=1, le=50),
    chart_type: str = Query("bar"),
    browser: str | None = Query(None),
):
    chart_type = normalize_chart_type(chart_type)
    browser_labels = available_browsers()
    browser = resolve_browser(request, browser, browser_labels)
    chart_data = build_chart_data(safe_history_counts(browser), limit) if browser_labels else []
    browser_label = browser_labels.get(browser, BROWSER_LABELS.get(browser, "выбранный браузер"))
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "chart": build_chart_model(chart_data, chart_type),
            "chart_labels": CHART_LABELS,
            "chart_type": chart_type,
            "browser": browser,
            "browser_label": browser_label,
            "browser_labels": browser_labels,
            "limit": limit,
            "total_visits": sum(item["visits"] for item in chart_data),
        },
    )


@router.get("/api/history")
def history_api(
    request: Request,
    limit: int = Query(TOP_SITES_LIMIT, ge=1, le=50),
    chart_type: str = Query("bar"),
    browser: str | None = Query(None),
) -> JSONResponse:
    chart_type = normalize_chart_type(chart_type)
    browser = resolve_browser(request, browser, available_browsers())
    chart_data = build_chart_data(safe_history_counts(browser), limit)
    return JSONResponse(
        {"limit": limit, "chart_type": chart_type, "browser": browser, "items": chart_data}
    )
