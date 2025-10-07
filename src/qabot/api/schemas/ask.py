from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class Timings(BaseModel):
    retrieve_ms: int
    llm_ms: int
    total_ms: int


class Source(BaseModel):
    title: str
    path: str
    updated_at: str


class Turn(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: List[Dict[str, str]]


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=512)
    session_id: Optional[str] = None
    history_summary: Optional[str] = None
    last_role: Optional[List[Turn]] = Field(default_factory=list)


class AskResponse(BaseModel):
    answer: str
    sources: List[Source]
    timings: Timings
