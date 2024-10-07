#!/bin/sh

uvicorn delivery_test_task.app.main:app --host 0.0.0.0 --port 8000 --workers 4 &
celery --app=delivery_test_task.worker.celery_app worker --beat --loglevel=info &
tail -f /dev/null




