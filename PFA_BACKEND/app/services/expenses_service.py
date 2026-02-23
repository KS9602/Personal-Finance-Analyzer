from math import ceil

from app.models.models import Users
from app.repositories.expenses_repository import ExpensesRepository
from app.schemas.expense_scheams import ExpenseDataPage

import logging

log = logging.getLogger(__name__)

class ExpensesService:
    def __init__(self,repo: ExpensesRepository):
        self.repo = repo


    async def get_user_expenses_page(self, user: Users, page: int, size: int) -> ExpenseDataPage:
        total = await self.repo.get_count_by_user(user.id)
        expenses = await self.repo.get_all_by_user_with_category(user.id, page, size)
        return ExpenseDataPage(
            items=expenses,
            total= total,
            page= page,
            size= size,
            total_pages = ceil(total / size)
        )