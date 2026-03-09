from datetime import date
from typing import Protocol

from app.models.models import Expenses, DashboardReport
from app.repositories.interfaces.IBaseRepository import IBaseRepository
from app.schemas.expense_scheams import DashboardDataCommand


class IExpenseRepository(IBaseRepository[Expenses], Protocol):

    async def get_all_by_user_with_category(self,user_id: int, page: int, size: int) -> list[Expenses]: ...
    async def get_expenses_by_category_and_date(self, cmd: DashboardDataCommand,): ...
    async def check_report_belongs_user(self, user_id: int, uuid: str) -> DashboardReport: ...
