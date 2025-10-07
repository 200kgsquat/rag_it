run_loader:
	uv run python -m scripts.run_loader

test_loader:
	uv run pytest -v tests/test_loader.py

format:
	uv run black src/ scripts/ tests/

run_chunker:
	uv run python -m scripts.run_chunker

test_chuncker:
	uv run pytest -v tests/test_chunker.py

run_indexer:
	uv run -m scripts.run_indexer

run_rag:
	uv run python -m scripts.run_rag

run_llm:
	uv run python -m scripts.run_llm "$(Q)"

run_api:
	uv run uvicorn src.qabot.api.main:app --host 0