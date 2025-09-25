import pytest
from src.qabot.ingest.loader import DocumentLoader, DocumentData


# Fixtures
@pytest.fixture
def loader():
    return DocumentLoader()


# Temporary directory for test files
@pytest.fixture
def tmp_files(tmp_path):
    # Markdown file
    md_file = tmp_path / "test.md"
    md_file.write_text(
        "# Markdown Title\nThis is a test markdown file.", encoding="utf-8"
    )

    # DOCX file
    from docx import Document as DocxDocument

    docx_file = tmp_path / "test.docx"
    doc = DocxDocument()
    doc.add_paragraph("This is a test DOCX file.")
    doc.save(docx_file)

    # PDF file
    from reportlab.pdfgen import canvas

    pdf_file = tmp_path / "test.pdf"
    c = canvas.Canvas(str(pdf_file))
    c.drawString(100, 750, "Hello PDF")
    c.save()

    return tmp_path


# Tests
def test_load_directory(loader, tmp_files):
    results = loader.load_directory(tmp_files)
    assert len(results) == 3, "Should load all three files"

    titles = [doc.title for doc in results]
    assert "test" in titles

    for doc in results:
        assert isinstance(doc, DocumentData)
        assert doc.text != ""
        assert doc.updated_at != ""
        assert doc.filetype in ["md", "docx", "pdf"]


def test_load_empty_directory(loader, tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    results = loader.load_directory(empty_dir)
    assert results == [], "Empty directory should return empty list"
