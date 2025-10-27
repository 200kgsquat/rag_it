from fastapi import Request
from src.qabot.llm.gateway import LLM
from src.qabot.search.retriever import Retriever
from src.qabot.repository.log_repository import LogRepository


def get_llm(request: Request) -> LLM:
    return request.app.state.llm


def get_retriever(request: Request) -> Retriever:
    return request.app.state.retriever


def get_log_repository(request: Request) -> LogRepository:
    return request.app.state.log_repository
