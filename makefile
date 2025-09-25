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
