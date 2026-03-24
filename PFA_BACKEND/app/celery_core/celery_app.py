from app.db.connection import SessionLocal
from celery import Celery

from app.core.config import settings
from app.celery_core.utils import BaseTask

BaseTask.sessionmaker = SessionLocal


celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
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
import app.celery_core.tasks.report_tasks