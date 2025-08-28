# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12-slim
FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY . .
RUN pip install --upgrade pip && pip install --no-cache-dir -e ".[mcp]"

RUN useradd -m app && chown -R app:app /app
USER app

# stdio: transport 指定なし（config 既定が stdio）
CMD ["python", "mcp_server.py"]

# HTTP用の設定（コメントアウト）
# EXPOSE 8009
# CMD ["python", "mcp_server.py", "--transport", "http", "--host", "0.0.0.0", "--port", "8009"]
