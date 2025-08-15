from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_process_init

from app.setup import redis_manager_sync, mongo_manager_sync
from app.config import settings


celery_instance = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    include=["app.tasks.tasks"],
)

celery_instance.conf.beat_schedule = {
    "task_1": {
        "task": "set_delivery_costs",
        "schedule": crontab(minute="*/5"),
    },
    "task_2": {
        "task": "set_usd_course",
        "schedule": crontab(minute="*/120"),
    },
    "task_3": {
        "task": "insert_buffer_to_mongo",
        "schedule": crontab(minute="*/5"),
    },
}


@worker_process_init.connect
def init_connections(**kwargs):
    mongo_manager_sync.connect()
    redis_manager_sync.connect()
