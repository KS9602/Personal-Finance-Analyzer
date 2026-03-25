from datetime import datetime, date, timedelta
from typing import List

from app.repositories.base_repository import BaseRepository
from app.models.models import Expenses, Users, DashboardReport, CeleryTask
from app.schemas.expense_scheams import DashboardDataCommand
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
import logging

log = logging.getLogger(__name__)


class ExpensesRepository(BaseRepository[Expenses]):
    model = Expenses


    async def get_all_by_user_with_category(self,user_id: int, page: int, size: int) -> List[Expenses]:
        stmt = (select(self.model)
                .options(selectinload(Expenses.expense_category))
                .where(self.model.user_id == user_id)
                .order_by(self.model.id.desc())
                .offset((page -1) * size)
                .limit(size)

        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_expenses_by_category_and_date(
            self,
            cmd: DashboardDataCommand,
    ):
        stmt = (
            select(
                self.model.date,
                func.sum(self.model.amount).label("amount")
                )
                .where(self.model.user_id == cmd.user_id)
                .where(self.model.date >= cmd.date_from)
                .where(self.model.date < cmd.date_to + timedelta(days=1))
                .group_by(self.model.date)
                .order_by(self.model.date.asc())
            )
        if cmd.category_id is not None:
            stmt = stmt.where(self.model.category_id == cmd.category_id)

        result = await self.session.execute(stmt)

        return result.all()

    async def check_report_belongs_user(self, user_id: int, uuid: str) -> DashboardReport:
        stmt = (
            select(CeleryTask)
            .join(DashboardReport, CeleryTask.task_id == DashboardReport.task_id)
            .where(
                DashboardReport.uuid == uuid,
                CeleryTask.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

