FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -U pip \
    && pip install -r requirements-dev.txt || true \
    && pip install pytest pytest-cov ruff black mypy

ENV PYTHONPATH=/app/src
CMD ["pytest", "-q"]

