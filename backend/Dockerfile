# Stage 1: dependencies
FROM python:3.12-slim AS deps
WORKDIR /app
# Install system deps needed by aiosqlite
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: runtime
FROM python:3.12-slim AS runtime
WORKDIR /app
# Create nonroot user
RUN groupadd -r app && useradd -r -g app app
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY app/ ./app/
COPY pyproject.toml .
# Use a volume for the SQLite database
VOLUME ["/app/data"]
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite+aiosqlite:///./data/observatory.db
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]