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
	export $(shell grep -v '^#' .env | xargs) && uv run uvicorn src.qabot.api.main:app --host 0

run_frontend:
	uv run streamlit run src/qabot/web/app.py

docker_build:
	sudo docker compose build

docker_up:
	sudo docker compose up

run_eval:
	uv run python -m evals.run_eval

test_eval:
	uv run pytest -v tests/test_eval.py

run_logs:
	uv run python -m scripts.fetch_logs $(ARGS)
