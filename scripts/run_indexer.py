import json
from src.qabot.indexer import Indexer
from src.qabot.search.retriever import Retriever
from config import config


def main():
    if not config.chunks_file.exists():
        raise FileNotFoundError(f"Chunks file not found: {config.chunks_file}")

    with config.chunks_file.open("r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks from {config.chunks_file}")

    indexer = Indexer(model_name=config.embedding_model)
    indexer.build_index(chunks)

    # Load indices and test both retrieval methods
    index_faiss, index_bm25, chunks_loaded = indexer.load()
    retriever = Retriever(config.embedding_model, index_faiss, chunks_loaded, index_bm25)

    query = "How to reset VPN password?"
    print(f"\nQuery: {query}")

    # Test semantic retrieval
    print("\n--- FAISS (Semantic) Results ---")
    faiss_results = retriever.retrieve(query, top_k=3)
    for i, res in enumerate(faiss_results, start=1):
        print(
            f"{i}. Score: {res['score']:.4f}, "
            f"Text: {res['text'][:150]}..., "
            f"Meta: {res['meta']}, "
            f"Chunk ID: {res['chunk_id']}"
        )

    # Test BM25 retrieval
    print(f"\n--- BM25 (Keyword) Results ---")
    bm25_results = retriever.bm25_retrieve(query, top_k=3)
    for i, res in enumerate(bm25_results, start=1):
        print(
            f"{i}. Score: {res['score']:.4f}, "
            f"Text: {res['text'][:150]}..., "
            f"Meta: {res['meta']}, "
            f"Chunk ID: {res['chunk_id']}"
        )


if __name__ == "__main__":
    main()
