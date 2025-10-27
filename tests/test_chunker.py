import pytest
from src.qabot.ingest.chunker import Chunker


@pytest.fixture
def sample_document():
    return {
        "title": "Test Document",
        "path": "data/test_doc.md",
        "text": """# Section 1
This is the first section. It has some text to tokenize.

More text in subsection one.

This is the second section, with additional content to test chunking.
""",
    }


def test_create_chunk_structure(sample_document):
    chunker = Chunker(max_tokens=20)
    chunks = chunker.chunk_document(sample_document)

    assert len(chunks) > 0, "Chunks should be created"
    for chunk in chunks:
        assert "id" in chunk
        assert "text" in chunk
        assert "meta" in chunk

        meta = chunk["meta"]
        for key in [
            "section_id",
            "sub_section_id",
            "section_title",
            "document_title",
            "path",
            "tokens",
        ]:
            assert key in meta


def test_chunk_token_limits(sample_document):
    chunker = Chunker(min_tokens=3, max_tokens=15, overlap_pct=0.2)
    chunks = chunker.chunk_document(sample_document)

    for chunk in chunks:
        tokens = chunk["meta"]["tokens"]
        assert tokens <= 15, f"Chunk too large: {tokens} tokens"
        assert tokens >= 1, f"Chunk too small: {tokens} tokens"


def test_chunk_overlap(sample_document):
    chunker = Chunker(max_tokens=10, overlap_pct=0.2)
    chunks = chunker.chunk_document(sample_document)

    for i in range(len(chunks) - 1):
        tokens_current = chunker.tokenizer.encode(chunks[i]["text"])
        tokens_next = chunker.tokenizer.encode(chunks[i + 1]["text"])

        overlap_tokens = int(len(tokens_current) * 0.2)
        if overlap_tokens > 0:
            overlap_in_next = sum(
                1 for t in tokens_current[-overlap_tokens:] if t in tokens_next
            )
            assert overlap_in_next >= 1, "Overlap not preserved"
