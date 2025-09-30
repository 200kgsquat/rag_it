from docx import Document as DocxDocument
from typing import List
from datetime import datetime
from pathlib import Path
from .models import DocumentData
import PyPDF2
import re


class DocumentLoader:
    def load_directory(self, directory_path: str) -> List[DocumentData]:
        documents = []
        path = Path(directory_path)

        if not path.exists() or not path.is_dir():
            raise ValueError(f"Directory not found: {directory_path}")

        for file_path in path.rglob("*"):
            if not file_path.is_file():
                continue

            if file_path.name.startswith(".") or file_path.name.endswith("~"):
                continue

            suffix = file_path.suffix.lower()
            if suffix == ".pdf":
                documents.append(self._load_pdf(file_path))
            elif suffix == ".docx":
                documents.append(self._load_docx(file_path))
            elif suffix == ".md":
                documents.append(self._load_markdown(file_path))

        return documents

    def _sanitize_text(self, text: str) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return ""

        if lines and re.match(
            r"^Updated:\s*\d{4}-\d{2}-\d{2}$", lines[-1], re.IGNORECASE
        ):
            lines.pop()

        return "\n".join(lines)

    def _load_markdown(self, file_path: Path) -> DocumentData:
        try:
            text = file_path.read_text(encoding="utf-8")
            text = self._sanitize_text(text)
            return self._create_document(file_path, text)
        except Exception as e:
            raise RuntimeError(
                f"Failed to load markdown file {file_path}: {e}"
            )

    def _load_pdf(self, file_path: Path) -> DocumentData:
        text = ""
        try:
            with file_path.open("rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            text = self._sanitize_text(text)
            return self._create_document(file_path, text)
        except Exception as e:
            raise RuntimeError(f"Failed to load PDF file {file_path}: {e}")

    def _load_docx(self, file_path: Path) -> DocumentData:
        try:
            doc = DocxDocument(file_path)
            text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            text = self._sanitize_text(text)
            return self._create_document(file_path, text)
        except Exception as e:
            raise RuntimeError(f"Failed to load DOCX file {file_path}: {e}")

    def _create_document(self, file_path: Path, text: str) -> DocumentData:
        title = file_path.stem
        filetype = file_path.suffix[1:]
        modified_time = file_path.stat().st_mtime
        updated_at = datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d")
        return DocumentData(
            title=title,
            path=str(file_path),
            filetype=filetype,
            updated_at=updated_at,
            text=text,
        )
