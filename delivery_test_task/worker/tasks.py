from .celery_app import celery_app

@celery_app.task
def periodic_task():
    print("Периодическая задача выполнена")