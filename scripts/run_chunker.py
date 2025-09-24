from src.qabot.ingest.loader import DocumentLoader
from src.qabot.ingest.chunker import Chunker
from tqdm import tqdm
import json
import os

INPUT_FOLDER = "data/it-knowledge/canonical"
OUTPUT_FILE = "data/chunks/chunks_updated.json"


def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    loader = DocumentLoader()
    documents = loader.load_directory(INPUT_FOLDER)
    print(f"Loaded {len(documents)} documents")

    chunker = Chunker(
        min_tokens=150,
        max_tokens=250,
        overlap_pct=0.15,
        min_chunk_length=15,
    )

    all_chunks = []
    for doc in tqdm(documents, desc="Chunking documents", unit="doc"):
        try:
            if doc.text.strip():
                chunks = chunker.chunk_document(
                    {"title": doc.title, "path": doc.path, "text": doc.text}
                )
                all_chunks.extend(chunks)
        except Exception as e:
            print(f"[ERROR] Failed to process document '{doc.title}': {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"Chunks saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
