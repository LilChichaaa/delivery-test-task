FROM python:3.11-alpine as builder

LABEL authors="Roman Mamin"

WORKDIR /delivery_test_task

RUN apk add --no-cache build-base

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-dev

FROM python:3.11-alpine

LABEL authors="Roman Mamin"

WORKDIR /delivery_test_task

COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "delivery_test_task.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
