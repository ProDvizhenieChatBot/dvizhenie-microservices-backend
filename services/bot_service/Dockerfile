FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

COPY pyproject.toml .

RUN groupadd -r app \
 && useradd -r -g app app \
 && chown -R app:app /app \
 && pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir .

COPY src .

USER app

ENTRYPOINT ["python", "-m", "app.main"]