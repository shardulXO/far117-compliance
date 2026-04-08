FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app/src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src
COPY server /app/server
COPY openenv.yaml /app/openenv.yaml
COPY pyproject.toml /app/pyproject.toml
COPY README.md /app/README.md

EXPOSE 7860

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
