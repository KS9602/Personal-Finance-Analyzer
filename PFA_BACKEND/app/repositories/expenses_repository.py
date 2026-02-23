from typing import Optional, List

from app.repositories.base_repository import BaseRepository
from app.models.models import Expenses, Users
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