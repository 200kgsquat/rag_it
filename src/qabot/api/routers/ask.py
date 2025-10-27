from fastapi import APIRouter, Request, Depends
import time
import uuid
from datetime import datetime, timezone
from src.qabot.llm.prompts import SYSTEM_PROMPT
from src.qabot.api.schemas import AskRequest, AskResponse
from src.qabot.api.dependencies.client import get_llm, get_retriever, get_log_repository
from src.qabot.repository.models import LogRecord

ask = APIRouter()


@ask.post("/ask", response_model=AskResponse)
async def ask_question(
    ask_request: AskRequest,
    llm=Depends(get_llm),
    retriever=Depends(get_retriever),
    log_repository=Depends(get_log_repository),
):

    session_id = ask_request.session_id or str(uuid.uuid4())

    t0 = time.time()
    context_chunks = retriever.retrieve(ask_request.question, top_k=3)
    t1 = time.time()


    seen_paths = set()
    unique_chunks = []
    for chunk in context_chunks:
        path = chunk["meta"].get("path")
        if path not in seen_paths:
            seen_paths.add(path)
            unique_chunks.append(chunk)

    context_texts = "\n\n".join(
        [f"- [Chunk {c['chunk_id']}] {c['text']}" for c in unique_chunks]
    )


    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Q: {ask_request.question}\n\nUse this context when answering:\n{context_texts}"}
    ]

    t2 = time.time()
    answer = llm.generate(messages=messages)
    t3 = time.time()

    timings = {
        "retrieve_ms": int((t1 - t0) * 1000),
        "llm_ms": int((t3 - t2) * 1000),
        "total_ms": int((t3 - t0) * 1000),
    }

    sources = [
        {
            "title": chunk["meta"].get("title", ""),
            "path": chunk["meta"].get("path", ""),
            "updated_at": chunk["meta"].get("updated_at", ""),
        }
        for chunk in unique_chunks
    ]

    top_doc_paths = [source["path"] for source in sources]
    answer_length = len(answer.split())
    log_record = LogRecord(
        timestamp=datetime.now(timezone.utc),
        session_id=session_id,
        question=ask_request.question,
        answer=answer,
        top_doc_paths=top_doc_paths,
        answer_length=answer_length,
        retrieve_ms=timings["retrieve_ms"],
        llm_ms=timings["llm_ms"],
        total_ms=timings["total_ms"],
    )
    log_repository.create(log_record)

    return AskResponse(answer=answer, sources=sources, timings=timings)
