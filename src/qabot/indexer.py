import pickle
import faiss
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from config import config


class Indexer:
    def __init__(self, model_name: str = None):
        if model_name is None:
            model_name = config.embedding_model
        self.model = SentenceTransformer(model_name)
        self.index: faiss.IndexFlatIP = None
        self.chunks = []

    def build_index(self, chunks: list):
        config.index_dir.mkdir(parents=True, exist_ok=True)
        self.chunks = chunks
        texts = [chunk["text"] for chunk in chunks]

        # Build FAISS index
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        faiss.normalize_L2(embeddings)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)
        faiss.write_index(self.index, str(config.index_file))

        # Build BM25 index
        tokenized_corpus = [self._tokenize(text) for text in texts]
        bm25 = BM25Okapi(tokenized_corpus)
        with config.bm25_file.open("wb") as f:
            pickle.dump(bm25, f)

        with config.index_chunks.open("wb") as f:
            pickle.dump(chunks, f)

        print(f"Index built: {self.index.ntotal} vectors")

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenization: lowercase and split on whitespace."""
        return text.lower().split()

    def load(self):
        index_faiss = faiss.read_index(str(config.index_file))
        with config.bm25_file.open("rb") as f:
            index_bm25 = pickle.load(f)
        with config.index_chunks.open("rb") as f:
            chunks = pickle.load(f)
        print(f"Indices loaded: FAISS ({index_faiss.ntotal} vectors), BM25 ({len(chunks)} docs)")
        return index_faiss, index_bm25, chunks

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
                        "chunk_id": idx,
                        "score": float(score),
                        "text": chunk["text"],
                        "meta": chunk.get("meta", {}),
                    }
                )
        return results
