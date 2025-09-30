from pathlib import Path

# Root
BASE_DIR = Path(__file__).resolve().parent

# Data
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "it-knowledge" / "canonical"
OUTPUT_FILE = DATA_DIR / "output" / "output.txt"
CHUNKS_FILE = DATA_DIR / "chunks" / "chunks_updated.json"

# Index
INDEX_DIR = BASE_DIR / ".index"
INDEX_FILE = INDEX_DIR / "index.faiss"
INDEX_CHUNKS = INDEX_DIR / "chunks_updated.pkl"

# Chunker config
CHUNKER_CONFIG = {
    "min_tokens": 150,
    "max_tokens": 250,
    "overlap_pct": 0.15,
    "min_chunk_length": 15,
}

# Embeding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
