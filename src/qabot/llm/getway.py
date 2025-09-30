import boto3
import json


class LLM:
    def __init__(self, model: str = "anthropic.claude-v2", region: str = "eu-north-1"):
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.model = model

    def generate(self, messages, temperature: float = 0.2, max_tokens: int = 512):
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt += f"\n\nHuman: {content}"
            elif role == "user":
                prompt += f"\n\nHuman: {content}"
            elif role == "assistant":
                prompt += f"\n\nAssistant: {content}"

        prompt += "\n\nAssistant:"

        body = json.dumps({
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens_to_sample": max_tokens
        })

        response = self.client.invoke_model(
            modelId=self.model,
            body=body
        )

        result = json.loads(response["body"].read())
        return result["completion"].strip()
