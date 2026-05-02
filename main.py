from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from routers.history import router as history_router


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Firefox History Website")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(history_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)