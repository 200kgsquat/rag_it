import json
import faiss
from typing import List, Dict
from src.qabot.llm.gateway import LLM
from src.qabot.llm.prompts import SYSTEM_PROMPT
from src.qabot.search.retriever import Retriever
from config import config


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


def run_rag():
    print("RAG assistant is ready. Type your question (or 'exit'):\n")
    while True:
        question = input("Q: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Exiting...")
            break

        top_chunks = retriever.retrieve(question, top_k=3)
        if not top_chunks:
            print("No relevant documents found.\n")
            continue

        context_texts = "\n\n".join(
            [
                f"- [Chunk {chunk['chunk_id']}] {chunk['text']}"
                for chunk in top_chunks
            ]
        )

        messages: List[Dict[str, str]] = [
            {
                "role": "user",
                "content": [
                    {
                        "text": f"Q: {question}\n\n"
                        f"Use this context when anwsering:\n{context_texts}"
                    }
                ],
            }
        ]

        try:
            answer = llm.generate(
                messages=messages, system=[{"text": SYSTEM_PROMPT}]
            )
            print(f"\nA: {answer}\n")
        except Exception as e:
            print(f"Error during LLM generation: {e}\n")


if __name__ == "__main__":
    run_rag()
