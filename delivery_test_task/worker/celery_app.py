from .. import settings
from celery import Celery
from celery.schedules import crontab

CELERY_BROKER_URL = settings.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = settings.CELERY_RESULT_BACKEND

celery_app = Celery(
    'delivery_test_task',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['delivery_test_task.worker.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    beat_schedule={
            'run-periodic-task-every-minute': {
                'task': 'delivery_test_task.worker.tasks.check_dollar_exchange_rate',
                'schedule': crontab(hour='*/24'),
            },
        }
)