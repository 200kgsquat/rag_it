from src.qabot.ingest.loader import DocumentLoader
from src.qabot.ingest.chunker import Chunker
from tqdm import tqdm
import json
import os
import config


def main():
    os.makedirs(os.path.dirname(config.CHUNKS_FILE), exist_ok=True)

    loader = DocumentLoader()
    documents = loader.load_directory(str(config.INPUT_DIR))
    print(f"Loaded {len(documents)} documents")

    chunker = Chunker(**config.CHUNKER_CONFIG)

    all_chunks = []
    for doc in tqdm(documents, desc="Chunking documents", unit="doc"):
        try:
            if doc.text.strip():
                chunks = chunker.chunk_document(doc)
                all_chunks.extend(chunks)
        except Exception as e:
            print(f"[ERROR] Failed to process document '{doc.title}': {e}")

    with open(config.CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            [chunk.model_dump() for chunk in all_chunks],
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"Chunks saved to {config.CHUNKS_FILE}")


if __name__ == "__main__":
    main()
