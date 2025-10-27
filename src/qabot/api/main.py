from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.qabot.api.routers.health import health
from src.qabot.api.routers.ask import ask
from src.qabot.api.routers.summarize import summarize
from src.qabot.indexer import Indexer
from src.qabot.llm.gateway import GroqClient
from src.qabot.search.retriever import Retriever
from src.qabot.repository.log_repository import LogRepository
import faiss
import json
from config import config
import logging

logger = logging.getLogger("api")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config.ensure_dirs()
    logger.info("Loading indices...")
    indexer = Indexer(model_name=config.embedding_model)
    index_faiss, index_bm25, chunks = indexer.load()
    retriever = Retriever(config.embedding_model, index_faiss, chunks, index_bm25)
    llm = GroqClient(model=config.llm.model)
    log_repository = LogRepository()
    app.state.retriever = retriever
    app.state.llm = llm
    app.state.log_repository = log_repository
    logger.info("✅ Resources initialized")
    yield
    logger.info("🛑 Resources cleaned up")


app = FastAPI(lifespan=lifespan)


app.include_router(health)
app.include_router(ask)
app.include_router(summarize)
