from datetime import datetime, date
from math import ceil
import uuid

from app.core.config import settings
from app.exceptions.exceptions import AuthorizationException
from app.models.models import Users, Expenses, TaskStatus
from app.repositories.expenses_repository import ExpensesRepository
from app.schemas.expense_scheams import (
    ExpenseDataPage,
    ExpenseCreate,
    ExpenseCharData,
    DashboardChartResponse,
)

import logging

from app.services.api_services.expense_categories_service import ExpenseCategoriesService
from asyncpg.pgproto.pgproto import timedelta
from fastapi import HTTPException
from starlette.responses import FileResponse

log = logging.getLogger(__name__)



class ExpensesService:
    def __init__(self,repo: ExpensesRepository, expense_categories_service: ExpenseCategoriesService):
        self._repo = repo
        self._expense_categories_service = expense_categories_service


    async def get_user_expenses_page(self, user: Users, page: int, size: int) -> ExpenseDataPage:
        total = await self._repo.get_count_by_user(user.id)
        expenses = await self._repo.get_all_by_user_with_category(user.id, page, size)
        return ExpenseDataPage(
            items=expenses,
            total= total,
            page= page,
            size= size,
            total_pages = ceil(total / size)
        )

    async def add_user_expense_response(self, user: Users, expense_create: ExpenseCreate) -> Expenses:
        expense_entity = Expenses(
            user_id = user.id,
            **expense_create.model_dump()
        )
        return await self._repo.add(expense_entity)


    async def delete_expense(self, user: Users, expense_id: int):
        expense_entity = await self._repo.get_by_id(expense_id)
        if not expense_entity or expense_entity.user_id != user.id:
            raise AuthorizationException(403)
        await self._repo.delete_by_id(expense_id)

    async def expense_chart(
            self,
            user: Users,
            category_id: int,
            date_from: datetime,
            date_to: datetime
    ):
        date_to, date_from = self.valid_chart_dates(date_to, date_from)
        if category_id and not await self._expense_categories_service.repo.exists(category_id):
            category_id = None

        result = await self._repo.get_expenses_by_category_and_date(
            user.id,
            category_id,
            date_from,
            date_to
        )
        return DashboardChartResponse(
            data = [
                ExpenseCharData(
                    date=row.date,
                    amount=row.amount
                )
                for row in result
            ]
        )

    async def delay_raport_generate(self,
            user: Users,
            category_id: int,
            date_from: date,
            date_to: date
    ):
        date_to, date_from = self.valid_chart_dates(date_from, date_to)
        if category_id and not self._expense_categories_service.repo.exists(category_id):
            category_id = None

        raport_uuid = str(uuid.uuid4())
        from app.celery_core.tasks.raport_tasks import generate_raport
        generate_raport.apply_async(
            args = [raport_uuid, user.id,category_id,date_from,date_to],
            headers = {
                "user_id" : user.id,
                "params" : {
                    "raport_uuid": raport_uuid,
                    "category_id": category_id,
                    "date_from": date_from.isoformat(),
                    "date_to": date_to.isoformat()
                }
            }
        )
        return {"raport_uuid" : raport_uuid}

    async def download_raport(self, user: Users, raport_uuid: str):
        raport_entity = await self._repo.check_raport_belongs_user(user.id, raport_uuid)
        if not raport_entity:
            raise HTTPException(status_code=404, detail="Raport not found")
        if raport_entity.status != TaskStatus.DONE:
            raise HTTPException(status_code=202, detail="Raport still generating")
        return FileResponse(
            path=f"{settings.DASHBOARD_RAPORTS_PATH}/{raport_uuid}.pdf",
            filename="raport.pdf",
            media_type="application/pdf"
        )


    def valid_chart_dates(self,date_from: date,date_to: date):
        if date_from > date_to:
            raise ValueError("Start date is latest than end date")
        if date_to is None:
            date_to = datetime.now()
        if date_from is None:
            date_from = date_to - timedelta(weeks=8)
        return date_to, date_from