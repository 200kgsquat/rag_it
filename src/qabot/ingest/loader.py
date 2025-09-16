from docx import Document as DocxDocument
from dataclasses import dataclass
from typing import List
from datetime import datetime
import os
import PyPDF2


@dataclass
class DocumentData:
    title: str
    path: str
    filetype: str
    updated_at: str
    text: str


class DocumentLoader:
    def load_directory(self, directory_path: str) -> List[DocumentData]:
        documents = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file.lower().endswith(".pdf"):
                    documents.append(self._load_pdf(file_path))
                elif file.lower().endswith(".docx"):
                    documents.append(self._load_docx(file_path))
                elif file.lower().endswith(".md"):
                    documents.append(self._load_markdown(file_path))
        return documents

    def _load_markdown(self, file_path: str) -> DocumentData:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return self._create_document(file_path, text)

    def _load_pdf(self, file_path: str) -> DocumentData:
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return self._create_document(file_path, text)

    def _load_docx(self, file_path: str) -> DocumentData:
        doc = DocxDocument(file_path)
        text = "\n".join(p.text for p in doc.paragraphs)
        return self._create_document(file_path, text)

    def _create_document(self, file_path: str, text: str) -> DocumentData:
        title = os.path.splitext(os.path.basename(file_path))[0]
        filetype = os.path.splitext(file_path)[1][1:]
        modified_time = os.path.getmtime(file_path)
        updated_at = datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d")
        return DocumentData(title, file_path, filetype, updated_at, text)
