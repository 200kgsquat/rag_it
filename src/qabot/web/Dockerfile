FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .
RUN pip install --upgrade pip && pip install uv && uv pip install --system .

COPY ./src/qabot/web ./src/qabot/web

EXPOSE 8501

CMD ["streamlit", "run", "src/qabot/web/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
