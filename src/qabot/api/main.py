from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.qabot.api.routers.health import health
from src.qabot.api.routers.ask import ask
from src.qabot.llm.gateway import LLM
from src.qabot.search.retriever import Retriever
import faiss
import json
from config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading FAISS index...")
    index = faiss.read_index(str(config.index_file))
    print("Loading chunks...")
    with config.chunks_file.open("r", encoding="utf-8") as f:
        chunks = json.load(f)
    retriever = Retriever(config.embedding_model, index, chunks)
    llm = LLM(
        model_id="arn:aws:bedrock:eu-north-1:437815003412:inference-profile/eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
        region="eu-north-1",
    )
    app.state.retriever = retriever
    app.state.llm = llm
    print("✅ Resources initialized")
    yield
    print("🛑 Resources cleaned up")


app = FastAPI(lifespan=lifespan)


app.include_router(health)
app.include_router(ask)
