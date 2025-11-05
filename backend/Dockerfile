FROM python:3.12-slim
WORKDIR /backend

# Set up dependencies
COPY poetry.lock pyproject.toml ./

# Install poetry and project dependencies
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the application code
COPY . .

EXPOSE 8000

RUN useradd --create-home backend
USER backend
 
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]