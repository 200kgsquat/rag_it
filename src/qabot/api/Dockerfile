FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .
RUN pip install --upgrade pip && pip install uv && uv pip install --system .

COPY ./src/qabot/api ./src/qabot/api
COPY ./src/qabot/llm ./src/qabot/llm
COPY ./src/qabot/search ./src/qabot/search
COPY ./src/qabot/ingest ./src/qabot/ingest
COPY ./src/qabot/indexer.py ./src/qabot/indexer.py
COPY ./config.py ./config.py
COPY ./data ./data

EXPOSE 8000

CMD ["uvicorn", "src.qabot.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
