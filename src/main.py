import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from api.v1.router import api_v1_router
from core.config import settings
from core.logging import setup_logger
from middleware.logging import LoggingMiddleware

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Service is starting up")

    if not os.path.exists(settings.CHROMA_PERSIST_DIRECTORY):
        logger.error(
            "ChromaDB persistence directory not found. "
            "Please run 'make pre-start' first to process and load the data."
        )
    yield
    logger.info("Service is shutting down ...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

app.include_router(api_v1_router, prefix=settings.API_V1_STR)
app.add_middleware(LoggingMiddleware)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(reqeust: Request):
    return templates.TemplateResponse(
        request=reqeust,
        name="index.html",
    )
