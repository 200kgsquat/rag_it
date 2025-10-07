import boto3
from typing import List, Dict


class LLM:
    def __init__(self, model_id: str, region: str = "eu-north-1"):
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.model_id = model_id

    def generate(
        self,
        messages: List[Dict[str, str]],
        system: List[Dict[str, str]] = [],
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> str:

        try:
            response = self.client.converse(
                modelId=self.model_id, messages=messages, system=system
            )

            return response["output"]["message"]["content"][0]["text"]
        except Exception as e:
            print(f"Error conversing model: {e}")
            raise
