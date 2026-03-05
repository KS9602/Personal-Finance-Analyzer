from typing import Any

from app.celery_core.celery_app import celery_app
import time

from app.services.chart_builder_service import create_chart, build_pdf


@celery_app.task(bind=True, max_retries=3)
async def generate_raport(self, user_id: str, category_id: int, data: list[dict[str, Any]]):
    try:
        user_data = None
        chart_data = None
        table_data = None
        build_pdf(user_data, category_id, chart_data, table_data)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)