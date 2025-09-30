import pickle
import faiss
from sentence_transformers import SentenceTransformer
import config


class Indexer:
    def __init__(self, model_name: str = None):
        if model_name is None:
            model_name = config.EMBEDDING_MODEL
        self.model = SentenceTransformer(model_name)
        self.index: faiss.IndexFlatIP = None
        self.chunks = []

    def build_index(self, chunks: list):
        config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
        self.chunks = chunks
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        faiss.normalize_L2(embeddings)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)
        faiss.write_index(self.index, str(config.INDEX_FILE))
        with config.INDEX_CHUNKS.open("wb") as f:
            pickle.dump(chunks, f)

        print(f"Index built: {self.index.ntotal} vectors")

    def load(self):
        """Load a previously saved FAISS index and chunks from disk."""
        self.index = faiss.read_index(str(config.INDEX_FILE))
        with open(config.INDEX_CHUNKS, "rb") as f:
            self.chunks = pickle.load(f)
        print(f"Index loaded: {self.index.ntotal} vectors")

    def query(self, query_text: str, k: int = 5):
        if self.index is None:
            raise ValueError("Index not built yet. Call build_index() first.")
        q_emb = self.model.encode([query_text], convert_to_numpy=True)
        faiss.normalize_L2(q_emb)
        scores, indices = self.index.search(q_emb, k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx]
                results.append(
                    {
                        "score": float(score),
                        "text": chunk["text"],
                        "meta": chunk["meta"],
                    }
                )
        return results
