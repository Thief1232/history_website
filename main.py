from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn

from routers.history import router as history_router


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app = FastAPI(title="Browser History Website")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(history_router)


@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code != 404 or request.url.path.startswith("/api/"):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    detail = exc.detail if isinstance(exc.detail, dict) else {}
    return templates.TemplateResponse(
        request,
        "404.html",
        {
            "title": detail.get("title", "Страница не найдена"),
            "message": detail.get("message", "Такой страницы нет."),
        },
        status_code=404,
    )

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
