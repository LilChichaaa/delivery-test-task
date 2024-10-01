FROM python:3.11-alpine as builder

LABEL authors="Roman Mamin"

WORKDIR /delivery_test_task

COPY pyproject.toml poetry.lock ./

RUN apk add --no-cache build-base postgresql-dev gcc musl-dev libpq && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

FROM python:3.11-alpine

LABEL authors="Roman Mamin"

WORKDIR /delivery_test_task

RUN apk add --no-cache libpq

COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "delivery_test_task.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
