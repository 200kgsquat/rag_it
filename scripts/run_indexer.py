from pathlib import Path
import json
from src.qabot.indexer import Indexer

CHUNKS_FILE = Path("data") / "chunks" / "chunks_updated.json"


def main():
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(f"Chunks file not found: {CHUNKS_FILE}")

    with CHUNKS_FILE.open("r", encoding="utf-8") as f:
        chunks = json.load(f)

    indexer = Indexer()
    print("Building FAISS index...")
    indexer.build_index(chunks)

    query = "How to reset VPN password?"
    print(f"\nQuery: {query}")
    results = indexer.query(query, k=3)

    for i, res in enumerate(results, start=1):
        print(
            f"{i}. Score: {res['score']:.4f}, "
            f"Text: {res['text'][:150]}..., "
            f"Meta: {res['meta']}"
        )


if __name__ == "__main__":
    main()
