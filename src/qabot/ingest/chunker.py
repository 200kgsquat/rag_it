import re
from typing import List, Dict
from sentence_transformers import SentenceTransformer


class Chunker:
    def __init__(
        self,
        tokenizer_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        min_tokens: int = 150,
        max_tokens: int = 250,
        overlap_pct: float = 0.15,
    ):
        self.tokenizer = SentenceTransformer(tokenizer_model_name).tokenizer
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.overlap_pct = overlap_pct

    def chunk_document(self, document: Dict) -> List[Dict]:
        sections = self._split_by_headings(document["text"])

        chunks = []
        for section_id, (heading, content) in enumerate(sections):
            section_chunks = self._split_by_tokens(
                content, document, section_id, heading
            )
            chunks.extend(section_chunks)

        return chunks

    def _split_by_headings(self, text: str) -> List[tuple]:
        pattern = r"(#{1,3})\s+(.*)"
        matches = list(re.finditer(pattern, text))
        if not matches:
            return [("", text)]

        sections = []
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            heading = match.group(2).strip()
            content = text[start:end].strip()
            sections.append((heading, content))
        return sections

    def _split_by_tokens(
        self, text: str, document: Dict, section_id: int, section_title: str
    ) -> List[Dict]:
        tokens = self.tokenizer.encode(text)
        total_tokens = len(tokens)
        if total_tokens <= self.max_tokens:
            return [
                self._create_chunk(
                    text, document, section_id, 0, section_title, total_tokens
                )
            ]

        chunks = []
        start_idx = 0
        sub_section_id = 0
        while start_idx < total_tokens:
            end_idx = min(start_idx + self.max_tokens, total_tokens)
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(
                self._create_chunk(
                    chunk_text,
                    document,
                    section_id,
                    sub_section_id,
                    section_title,
                    len(chunk_tokens),
                )
            )
            overlap = int(len(chunk_tokens) * self.overlap_pct)
            start_idx = end_idx - overlap
            sub_section_id += 1
        return chunks

    def _create_chunk(
        self,
        text: str,
        document: Dict,
        section_id: int,
        sub_section_id: int,
        section_title: str,
        token_count: int,
    ) -> Dict:
        doc_title_slug = document["title"].replace(" ", "-").lower()
        chunk_id = f"{doc_title_slug}_{section_id}_{sub_section_id}"
        return {
            "id": chunk_id,
            "text": text,
            "meta": {
                "section_id": str(section_id),
                "sub_section_id": str(sub_section_id),
                "section_title": section_title,
                "document_title": document["title"],
                "path": document["path"],
                "tokens": token_count,
            },
        }
