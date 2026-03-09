from datetime import datetime, date

from app.celery_core.celery_app import celery_app
from app.celery_core.utils import BaseTask
from app.schemas.expense_scheams import DashboardDataCommand
from app.services.internal_services.dashboard_report_service import DashboardReportService



@celery_app.task(bind=True, base=BaseTask ,max_retries=3)
def generate_report(
        self,
        report_uuid: str,
        user_id: int,
        category_id: int,
        date_from: date,
        date_to: date
):
    command = DashboardDataCommand(
        user_id=user_id,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to
    )
    try:
        dashboard_report_service = DashboardReportService(self.session)
        dashboard_report_service.build_report(self.task_id, report_uuid, command)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)