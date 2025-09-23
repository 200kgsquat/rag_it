import os
import json
from tqdm import tqdm
from src.qabot.ingest.chunker import Chunker

INPUT_FOLDER = "data/output"
OUTPUT_FILE = "data/chunks/chunks_updated.json"


def load_documents(input_folder: str):
    """Load and parse documents from .txt files"""
    documents = []
    for file_name in os.listdir(input_folder):
        if not file_name.endswith(".txt"):
            continue

        file_path = os.path.join(input_folder, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"[WARN] Could not read {file_path}: {e}")
            continue

        for entry in content.split("=== "):
            if not entry.strip():
                continue

            lines = entry.splitlines()
            if not lines:
                continue

            title_line = lines[0].strip(" =")
            metadata = {}
            text_lines = []

            for line in lines[1:]:
                stripped = line.strip()
                if stripped.startswith("Path:"):
                    metadata["path"] = stripped.replace("Path:", "", 1).strip()
                elif stripped.startswith("Type:"):
                    metadata["type"] = stripped.replace("Type:", "", 1).strip()
                elif stripped.startswith("Updated:"):
                    metadata["updated"] = stripped.replace(
                        "Updated:", "", 1
                    ).strip()
                elif (
                    stripped.startswith("Text length:") or "-----" in stripped
                ):
                    continue
                else:
                    text_lines.append(line)

            text = "\n".join(text_lines).strip()
            if not text:
                continue

            documents.append(
                {
                    "title": title_line,
                    "path": metadata.get("path", file_path),
                    "text": text,
                }
            )

    return documents


def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    documents = load_documents(INPUT_FOLDER)
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
            if doc["text"].strip():
                chunks = chunker.chunk_document(doc)
                all_chunks.extend(chunks)
        except Exception as e:
            print(f"[ERROR] Failed to process document '{doc['title']}': {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"Chunks saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
