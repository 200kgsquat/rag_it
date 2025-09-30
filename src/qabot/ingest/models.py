from pydantic import BaseModel
from typing import Optional


class DocumentData(BaseModel):

    title: str
    path: str
    text: str
    filetype: str
    updated_at: str


class Chunk(BaseModel):
    id: str
    text: str
    meta: dict
    document: Optional[DocumentData] = None
