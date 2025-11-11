FROM public.ecr.aws/lambda/python:3.12

# Set up dependencies
COPY poetry.lock pyproject.toml ${LAMBDA_TASK_ROOT}
# Install poetry and project dependencies
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root 

# Copy the rest of the application code
COPY . ${LAMBDA_TASK_ROOT}

CMD ["main.handler"]