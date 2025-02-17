import pickle
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from api.v1.router import api_v1_router
from core.config import settings
from core.logging import setup_logger
from domain.knowledge import FAQ
from repositories.knowledge import ChromaKnowledgeRepository

logger = setup_logger(__name__)


def load_faq_data(file_path: str = "data/faq_processed.pkl") -> list[FAQ]:
    with open(file_path, "rb") as f:
        raw_faqs = pickle.load(f)

    return [
        FAQ(
            question=question,
            clean_question=data["clean_question"],
            answer=data["answer"],
            tags=data.get("tags", []),
        )
        for question, data in raw_faqs.items()
    ]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Service is starting up")
    try:
        # ChromaDB 초기화
        knowledge_repo = ChromaKnowledgeRepository()
        if knowledge_repo.collection.count() == 0:
            # FAQ 데이터 로드
            faqs = load_faq_data()
            logger.info(f"Loading {len(faqs)} FAQs into ChromaDB...")
            await knowledge_repo.bulk_add_faqs(faqs)
            logger.info("FAQ data loaded successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise

    yield

    logger.info("Service is shutting down ...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

app.include_router(api_v1_router, prefix=settings.API_V1_STR)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(reqeust: Request):
    return templates.TemplateResponse(
        request=reqeust,
        name="index.html",
    )
