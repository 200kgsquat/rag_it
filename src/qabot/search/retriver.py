from typing import List, Dict
import faiss
from sentence_transformers import SentenceTransformer


class Retriever:
    def __init__(
        self, model_name: str, index: faiss.Index, chunks: List[Dict]
    ):
        self.model = SentenceTransformer(model_name)
        self.index = index
        self.chunks = chunks

    def retrieve(self, question: str, top_k: int = 3) -> List[Dict]:
        if not question.strip():
            return []

        # Embed + normalize
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
