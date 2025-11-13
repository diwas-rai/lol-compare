FROM python:3.12 AS builder

RUN pip install poetry
WORKDIR /usr/src/app

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.in-project true \
    && poetry install --no-root --without dev

FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY --from=builder /usr/src/app/.venv ./.venv

COPY main.py config.py schemas.py dependencies.py ./
COPY routers ./routers
COPY assets ./assets

ENV PYTHONPATH="${LAMBDA_TASK_ROOT}/.venv/lib/python3.12/site-packages"
ENV PATH="${LAMBDA_TASK_ROOT}/.venv/bin:${PATH}"
ENV VIRTUAL_ENV="${LAMBDA_TASK_ROOT}/.venv"

CMD ["main.handler"]