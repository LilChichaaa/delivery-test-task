FROM alpine:3.19 as builder

LABEL authors="Roman Mamin"

WORKDIR /delivery_test_task

RUN apk add --no-cache python3=~3.11 py3-pip bash && \
    apk add --update --no-cache --virtual .build-deps build-base python3-dev && \
    python3 -m venv /venv && \
    /venv/bin/python3 -m pip install poetry

COPY . .

RUN /venv/bin/poetry install --no-dev

ENV PATH="/venv/bin:$PATH"

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "delivery_test_task.app.main:app", "--reload"]