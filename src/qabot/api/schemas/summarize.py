from pydantic import BaseModel
from typing import List, Optional

class SummarizeRequest(BaseModel):
    session_id: Optional[str]
    chat_history: List[dict]
