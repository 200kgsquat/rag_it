from fastapi import APIRouter, Request
import time
from src.qabot.llm.prompts import SYSTEM_PROMPT
from src.qabot.api.schemas import AskRequest, AskResponse

ask = APIRouter()


@ask.post("/ask", response_model=AskResponse)
async def ask_question(ask_request: AskRequest, request: Request):
    retriever = request.app.state.retriever
    llm = request.app.state.llm
    context_chunks = retriever.retrieve(ask_request.question, top_k=3)

    context_texts = "\n\n".join(
        [
            f"- [Chunk {chunk['chunk_id']}] {chunk['text']}"
            for chunk in context_chunks
        ]
    )

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "text": f"Q: {ask_request.question}\n\nUse this context when anwsering:\n{context_texts}"
                }
            ],
        }
    ]

    t0 = time.time()
    answer = llm.generate(messages=messages, system=[{"text": SYSTEM_PROMPT}])
    t1 = time.time()

    timings = {
        "retrieve_ms": 0,
        "llm_ms": int((t1 - t0) * 1000),
        "total_ms": int((t1 - t0) * 1000),
    }

    sources = [
        {
            "title": chunk["meta"].get("title", ""),
            "path": chunk["meta"].get("path", ""),
            "updated_at": chunk["meta"].get("updated_at", ""),
        }
        for chunk in context_chunks
    ]

    return AskResponse(answer=answer, sources=sources, timings=timings)
