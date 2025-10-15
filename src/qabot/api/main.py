from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.qabot.api.routers.health import health
from src.qabot.api.routers.ask import ask
from src.qabot.api.routers.summarize import summarize
from src.qabot.llm.gateway import GroqClient
from src.qabot.search.retriever import Retriever
import faiss
import json
from config import config
import logging

logger = logging.getLogger("api")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading FAISS index...")
    index = faiss.read_index(str(config.index_file))
    logger.info("Loading chunks...")
    with config.chunks_file.open("r", encoding="utf-8") as f:
        chunks = json.load(f)
    retriever = Retriever(config.embedding_model, index, chunks)
    llm = GroqClient(model=config.llm.model)
    app.state.retriever = retriever
    app.state.llm = llm
    logger.info("✅ Resources initialized")
    yield
    logger.info("🛑 Resources cleaned up")


app = FastAPI(lifespan=lifespan)


app.include_router(health)
app.include_router(ask)
app.include_router(summarize)
