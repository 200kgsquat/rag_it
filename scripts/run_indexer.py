import json
from src.qabot.indexer import Indexer
from config import config


def main():
    if not config.chunks_file.exists():
        raise FileNotFoundError(f"Chunks file not found: {config.chunks_file}")

    with config.chunks_file.open("r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks from {config.chunks_file}")

    indexer = Indexer(model_name=config.embedding_model)
    indexer.build_index(chunks)

    query = "How to reset VPN password?"
    print(f"\nQuery: {query}")
    results = indexer.query(query, k=3)

    for i, res in enumerate(results, start=1):
        print(
            f"{i}. Score: {res['score']:.4f}, "
            f"Text: {res['text'][:150]}..., "
            f"Meta: {res['meta']}, "
            f"Chunk ID: {res['chunk_id']}"
        )


if __name__ == "__main__":
    main()
