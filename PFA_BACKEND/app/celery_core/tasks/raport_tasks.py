from datetime import datetime


from app.celery_core.celery_app import celery_app
from app.celery_core.utils import BaseTask
from app.services.internal_services.dashboard_raport_service import DashboardReportService



@celery_app.task(bind=True, base=BaseTask ,max_retries=3)
def generate_raport(
        self,
        raport_uuid: str,
        user_id: int,
        category_id: int,
        date_from: datetime,
        date_to: datetime
):
    try:
        dashboard_raport_service = DashboardReportService(self.session)
        dashboard_raport_service.build_raport(self.task_id, raport_uuid, user_id, category_id, date_from, date_to)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)