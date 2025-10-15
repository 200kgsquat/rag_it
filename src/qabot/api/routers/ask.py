from fastapi import APIRouter, Request, Depends
import time
from src.qabot.llm.prompts import SYSTEM_PROMPT
from src.qabot.api.schemas import AskRequest, AskResponse
from src.qabot.api.dependencies.client import get_llm, get_retriever

ask = APIRouter()


@ask.post("/ask", response_model=AskResponse)
async def ask_question(
    ask_request: AskRequest,
    llm=Depends(get_llm),
    retriever=Depends(get_retriever),
):
    # Measure retrieval time
    t0 = time.time()
    context_chunks = retriever.retrieve(ask_request.question, top_k=3)
    t1 = time.time()

    # Remove duplicate documents
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

    return AskResponse(answer=answer, sources=sources, timings=timings)
