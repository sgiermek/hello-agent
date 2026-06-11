from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import APP_ENV, APP_VERSION

app = FastAPI(title="Hello Agent's World")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_env": APP_ENV, "app_version": APP_VERSION},
    )


@app.get("/health")
async def health():
    return {"status": "ok", "env": APP_ENV, "version": APP_VERSION}
