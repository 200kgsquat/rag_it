import sys
from src.qabot.llm.gateway import LLM

if len(sys.argv) < 2:
    print("Usage: python scripts/run_llm.py 'Your question here'")
    sys.exit(1)

question = sys.argv[1]
llm = LLM(
    model_id="arn:aws:bedrock:eu-north-1:437815003412:inference-profile/eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
    region="eu-north-1",
)

messages = [{"role": "user", "content": [{"text": question}]}]

try:
    answer = llm.generate(messages=messages)
    print(f"A: {answer}")
except Exception as e:
    print(f"Error during LLM generation: {e}")
