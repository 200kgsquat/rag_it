from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class LogRecord(BaseModel):
    id: Optional[int] = None
    timestamp: datetime
    session_id: str
    question: str
    answer: str
    top_doc_paths: List[str]
    answer_length: int  # in tokens
    retrieve_ms: int
    llm_ms: int
    total_ms: int
