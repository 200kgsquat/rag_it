from src.qabot.ingest.loader import DocumentLoader
from src.qabot.ingest.chunker import Chunker
from config import config
from tqdm import tqdm
import json


def main():
    config.ensure_dirs()

    loader = DocumentLoader()
    documents = loader.load_directory(str(config.input_dir))
    print(f"Loaded {len(documents)} documents")

    chunker = Chunker(
        min_tokens=config.chunker.min_tokens,
        max_tokens=config.chunker.max_tokens,
        overlap_pct=config.chunker.overlap_pct,
        min_chunk_length=config.chunker.min_chunk_length,
    )

    all_chunks = []
    for doc in tqdm(documents, desc="Chunking documents", unit="doc"):
        try:
            if doc.text.strip():
                chunks = chunker.chunk_document(doc)
                all_chunks.extend(chunks)
        except Exception as e:
            print(f"[ERROR] Failed to process document '{doc.title}': {e}")

    with open(config.chunks_file, "w", encoding="utf-8") as f:
        json.dump(
            [chunk.model_dump() for chunk in all_chunks],
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Chunks saved to {config.chunks_file}")


if __name__ == "__main__":
    main()
