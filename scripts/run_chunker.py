import os
from src.qabot.ingest.chunker import Chunker
import json

input_folder = "data/output"
output_file = "data/chunks/chunks_updated.json"

os.makedirs("data/chunks", exist_ok=True)

documents = []

for file_name in os.listdir(input_folder):
    if file_name.endswith(".txt"):
        file_path = os.path.join(input_folder, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        entries = content.split("=== ")
        for entry in entries:
            if not entry.strip():
                continue
            lines = entry.splitlines()
            title_line = lines[0].strip(" =")
            metadata = {}
            text_lines = []
            for line in lines[1:]:
                if line.startswith("Path:"):
                    metadata["path"] = line.replace("Path:", "").strip()
                elif line.startswith("Type:"):
                    metadata["type"] = line.replace("Type:", "").strip()
                elif line.startswith("Updated:"):
                    metadata["updated"] = line.replace("Updated:", "").strip()
                elif line.startswith("Text length:"):
                    continue
                elif line.startswith(
                    "--------------------------------------------------"
                ):
                    continue
                else:
                    text_lines.append(line)
            text = "\n".join(text_lines).strip()
            documents.append(
                {
                    "title": title_line,
                    "path": metadata.get("path", ""),
                    "text": text,
                }
            )

print(f"Loaded {len(documents)} documents")

chunker = Chunker(min_tokens=150, max_tokens=250, overlap_pct=0.15)
all_chunks = []
for doc in documents:
    if doc["text"]:
        chunks = chunker.chunk_document(doc)
        all_chunks.extend(chunks)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, ensure_ascii=False, indent=2)

print(f"Chunks saved to {output_file}")
