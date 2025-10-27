from typing import List, Dict
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class Retriever:
    def __init__(
        self, model_name: str, index: faiss.Index, chunks: List[Dict], index_bm25=None
    ):
        self.model = SentenceTransformer(model_name)
        self.index = index
        self.chunks = chunks
        self.index_bm25 = index_bm25

    def retrieve(self, question: str, top_k: int = 3) -> List[Dict]:
        if not question.strip():
            return []

                           
        q_emb = self.model.encode([question], convert_to_numpy=True)
        faiss.normalize_L2(q_emb)

        scores, indices = self.index.search(q_emb, top_k)

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

    def bm25_retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        if not query.strip():
            return []
        if self.index_bm25 is None:
            raise ValueError("BM25 index not available")

        # Simple tokenization matching indexer
        tokenized_query = query.lower().split()
        scores = self.index_bm25.get_scores(tokenized_query)

        # Get top-k indices and scores
        top_indices = np.argsort(scores)[::-1][:top_k]
        top_scores = scores[top_indices]

        results = []
        for idx, score in zip(top_indices, top_scores):
            if idx < len(self.chunks):
                chunk = self.chunks[idx]
                results.append(
                    {
                        "chunk_id": int(idx),
                        "score": float(score),
                        "text": chunk["text"],
                        "meta": chunk.get("meta", {}),
                    }
                )
        return results
