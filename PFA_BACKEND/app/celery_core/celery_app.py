import os
from celery import Celery

from app.core.config import settings

broker_url = os.getenv(
    "CELERY_BROKER_URL",
    settings.CELERY_BROKER_URL
)

celery_app = Celery(
    "worker",
    broker=broker_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Warsaw",
    enable_utc=True,
)
celery_app.autodiscover_tasks([
    "app.celery_core.tasks"
])
import app.celery_core.tasks.raport_tasks