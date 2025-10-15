from typing import List, Optional
from pydantic import BaseModel, Field


class Usage(BaseModel):
    queue_time: float
    prompt_tokens: int
    prompt_time: float
    completion_tokens: int
    completion_time: float
    total_tokens: int
    total_time: float


class Timings(BaseModel):
    retrieve_ms: int
    llm_ms: int
    total_ms: int


class GroqChoiceMessage(BaseModel):
    role: str
    content: str

class GroqChoice(BaseModel):
    index: int
    message: GroqChoiceMessage
    logprobs: Optional[dict] = None
    finish_reason: Optional[str] = None

class GroqXGroq(BaseModel):
    id: str

class AskResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[GroqChoice]
    usage: Usage
    system_fingerprint: Optional[str] = None
    x_groq: Optional[GroqXGroq] = None


class Source(BaseModel):
    title: str
    path: str
    updated_at: str


class Turn(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str


class AskRequest(BaseModel):
    session_id: Optional[str] = None
    question: str = Field(min_length=3, max_length=512)
    history_summary: Optional[str] = None
    last_turns: List[Turn] = Field(default_factory=list)


class AskResponse(BaseModel):
    answer: str
    sources: List[Source]
    timings: Timings
