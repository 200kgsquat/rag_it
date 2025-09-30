import re
import tiktoken
from typing import List, Tuple
from .models import DocumentData, Chunk


class Chunker:
    def __init__(
        self,
        min_tokens: int = 150,
        max_tokens: int = 240,
        overlap_pct: float = 0.15,
        min_chunk_length: int = 15,
    ):
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.overlap_pct = overlap_pct
        self.min_chunk_length = min_chunk_length

    def chunk_document(self, document: DocumentData) -> List[Chunk]:
        text = document.text.strip()
        if not text:
            return []

        text = re.sub(r"[^\x20-\x7E\n\r\t]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        sections = self._split_by_headings(text)
        chunks: List[Chunk] = []

        for section_id, (heading, content) in enumerate(sections):
            chunks.extend(
                self._split_by_tokens(content, document, section_id, heading)
            )

        return [c for c in chunks if c]

    def _split_by_headings(self, text: str) -> List[Tuple[str, str]]:
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
        self,
        text: str,
        document: DocumentData,
        section_id: int,
        section_title: str,
    ) -> List[Chunk]:
        if not text.strip():
            return []

        tokens = self.tokenizer.encode(text)
        n = len(tokens)

        if n <= self.max_tokens:
            return [
                self._create_chunk(
                    text, document, section_id, 0, section_title, n
                )
            ]

        chunks: List[Chunk] = []
        start_idx = 0
        sub_section_id = 0
        overlap = int(self.max_tokens * self.overlap_pct)

        while start_idx < n:
            end_idx = min(start_idx + self.max_tokens, n)
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.tokenizer.decode(chunk_tokens).strip()

            if len(chunk_text) >= self.min_chunk_length:
                token_count = len(chunk_tokens)
                if token_count >= self.min_tokens:
                    chunks.append(
                        self._create_chunk(
                            chunk_text,
                            document,
                            section_id,
                            sub_section_id,
                            section_title,
                            token_count,
                        )
                    )
                    sub_section_id += 1

            start_idx = end_idx - overlap if end_idx < n else n

        return chunks

    def _create_chunk(
        self,
        text: str,
        document: DocumentData,
        section_id: int,
        sub_section_id: int,
        section_title: str,
        token_count: int,
    ) -> Chunk:
        doc_title_slug = document.title.replace(" ", "-").lower()
        chunk_id = f"{doc_title_slug}_{section_id}_{sub_section_id}"
        return Chunk(
            id=chunk_id,
            text=text,
            meta={
                "section_id": str(section_id),
                "sub_section_id": str(sub_section_id),
                "section_title": section_title,
                "document_title": document.title,
                "path": document.path,
                "tokens": token_count,
            },
            document=document,
        )
