import os
import requests
from typing import List, Dict, Optional
from .base import LLM
from config import config


class GroqClient(LLM):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 30,
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY must be set")

        self.base_url = (base_url or config.llm.base_url).rstrip("/")
        self.model = model or config.llm.model
        self.timeout = timeout

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> str:
                                       
        formatted_messages = []
        for msg in messages:
            if "role" not in msg or "content" not in msg:
                raise ValueError("Each message must have 'role' and 'content' fields")
            
            role = msg["role"]
            content = msg["content"]
            
                                
            if isinstance(content, list):
                                                          
                content_parts = []
                for item in content:
                    if isinstance(item, dict) and "text" in item:
                        content_parts.append(item["text"])
                    elif isinstance(item, str):
                        content_parts.append(item)
                content = " ".join(content_parts)
            elif not isinstance(content, str):
                content = str(content)
            
                                         
            if not content.strip():
                continue
                
            formatted_messages.append({
                "role": role,
                "content": content.strip()
            })

                                           
        if not formatted_messages:
            raise ValueError("No valid messages to send")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": max(0.0, min(temperature, 2.0)),                         
            "max_tokens": max(1, min(max_tokens, 4096)),                       
            "stream": False,                                  
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            
                                        
            if resp.status_code != 200:
                error_detail = f"Status: {resp.status_code}"
                try:
                    error_data = resp.json()
                    if "error" in error_data:
                        error_detail += f", Message: {error_data['error'].get('message', 'Unknown error')}"
                except:
                    error_detail += f", Response: {resp.text}"
                
                raise requests.HTTPError(error_detail)
                
            data = resp.json()
            
        except requests.RequestException as e:
            raise RuntimeError(f"Error calling Groq API: {e}") from e

        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Unexpected response format from Groq API: {data}") from e