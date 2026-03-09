from datetime import date
from typing import Protocol

from app.models.models import Expenses, DashboardRaport
from app.repositories.interfaces.IBaseRepository import IBaseRepository


class IExpenseRepository(IBaseRepository[Expenses], Protocol):

    async def get_all_by_user_with_category(self,user_id: int, page: int, size: int) -> list[Expenses]: ...
    async def get_expenses_by_category_and_date(
            self,
            user_id: int,
            category: str | None,
            date_scope_start: date,
            date_scope_end: date
    ): ...
    async def check_raport_belongs_user(self, user_id: int, uuid: str) -> DashboardRaport: ...
