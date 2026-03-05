from datetime import date, datetime
from math import ceil

from app.celery_core.utils import save_task
from app.exceptions.exceptions import AuthorizationException
from app.models.models import Users, Expenses
from app.repositories.expenses_repository import ExpensesRepository
from app.schemas.expense_scheams import (
    ExpenseDataPage,
    ExpenseCreate,
    ExpenseCharData,
    DashboardChartResponse,
    RaportGenerateResponse
)

import logging

from app.services.expense_categories_service import ExpenseCategoriesService
from asyncpg.pgproto.pgproto import timedelta

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
        if date_to is None:
            date_to = datetime.now()
        if date_from is None:
            date_from = date_to - timedelta(weeks=8)

        if category_id and not await self._expense_categories_service.repo.exists(category_id):
            category_id = None
        if date_from > date_to:
            raise ValueError("Start date is latest than end date")

        result = await self._repo.get_expenses_by_category_and_date(
            user.id,
            category_id,
            date_from,
            date_to
        )
        await self.delay_raport_generate(
            user,
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
            date_from: datetime,
            date_to: datetime
    ):
        if date_from > date_to:
            raise ValueError("Start date is latest than end date")
        if date_to is None:
            date_to = datetime.now()
        if date_from is None:
            date_from = date_to - timedelta(weeks=8)
        if category_id and not self._expense_categories_service.repo.exists(category_id):
            category_id = None

        result = await self._repo.get_expenses_by_category_and_date(
            user.id,
            category_id,
            date_from,
            date_to
        )

        from app.celery_core.tasks.raport_tasks import generate_raport
        task = generate_raport.delay(
            user.id,
            category_id,
            data = [
                {
                    "date":row.date,
                    "amount":row.amount
                }
                for row in result
            ]
        )
        await save_task(
            task_id=task.id,
            user_id= user.id,
            task_type= "DASHBOARD_RAPORT",                   # jakies repo na typy, glowny slownik
            params = {
                "category_id":category_id,
                "date_from":date_from.isoformat(),
                "date_to":date_to.isoformat()
            }
        )
        return RaportGenerateResponse(task_id=task.id)
