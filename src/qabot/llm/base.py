from abc import ABC, abstractmethod
from typing import List, Dict


class LLM(ABC):

    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        system: List[Dict[str, str]] = [],
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> str:
        pass
