import json
from src.qabot.indexer import Indexer
import config


def main():
    if not config.CHUNKS_FILE.exists():
        raise FileNotFoundError(f"Chunks file not found: {config.CHUNKS_FILE}")

    with config.CHUNKS_FILE.open("r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks from {config.CHUNKS_FILE}")

    indexer = Indexer(model_name=config.EMBEDDING_MODEL)
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
