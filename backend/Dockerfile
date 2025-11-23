FROM python:3.12 AS builder

RUN pip install poetry
WORKDIR /usr/src/app

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.in-project true \
    && poetry install --no-root --without dev

FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY --from=builder /usr/src/app/.venv ./.venv

COPY assets ./assets

COPY app ./app

# Set Environment Variables
ENV PYTHONPATH="${LAMBDA_TASK_ROOT}/.venv/lib/python3.12/site-packages"
ENV PATH="${LAMBDA_TASK_ROOT}/.venv/bin:${PATH}"
ENV VIRTUAL_ENV="${LAMBDA_TASK_ROOT}/.venv"

# IMPORTANT:
# Since main.py is now inside the 'app' package, the handler path changes.
# Format: package.module.function
CMD ["app.main.handler"]