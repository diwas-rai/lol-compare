FROM python:3.12-slim AS build

WORKDIR /app

RUN pip install poetry

RUN poetry config virtualenvs.in-project true

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-root


FROM python:3.12-slim

WORKDIR /app

COPY --from=build /app/.venv .venv

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]