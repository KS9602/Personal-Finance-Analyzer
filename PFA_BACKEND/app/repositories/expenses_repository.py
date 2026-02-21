from typing import Optional

from app.repositories.base_repository import BaseRepository
from app.models.models import Expenses, Users
from sqlalchemy import select, func


class ExpensesRepository(BaseRepository[Expenses]):
    model = Expenses

    async def get_expenses_page(
            self,
            user_id: int,
            page: int,
            size: int,
    ) -> tuple[list[Expenses], int]:

        total = await self.get_count_by_user(user_id)
        items = await self.get_all_by_user_page(user_id, page, size)
        return items, total