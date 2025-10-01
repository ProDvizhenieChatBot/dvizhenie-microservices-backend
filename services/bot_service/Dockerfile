# Stage 1: Build the virtual environment using uv
FROM python:3.12-slim AS builder

RUN pip install --no-cache-dir uv

RUN uv venv /opt/venv

WORKDIR /app
COPY pyproject.toml .

RUN uv pip install --no-cache --python /opt/venv/bin/python .


FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH=/app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

RUN groupadd -r app \
 && useradd -r -g app app

COPY src .

RUN chown -R app:app /app

USER app

# The python executable is from the venv
ENTRYPOINT ["python", "-m", "app.main"]