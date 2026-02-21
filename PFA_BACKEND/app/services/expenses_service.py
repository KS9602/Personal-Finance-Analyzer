from math import ceil

from app.models.models import Users
from app.repositories.expenses_repository import ExpensesRepository
from app.schemas.schemas import ExpenseDataPage

import logging

log = logging.getLogger(__name__)

class ExpensesService:
    def __init__(self,repo: ExpensesRepository):
        self.repo = repo


    async def get_user_expenses_page(self, user: Users, page: int, size: int):
        expenses, total = await self.repo.get_expenses_page(user.id, page, size)
        return ExpenseDataPage(
            items=expenses,
            total= total,
            page= page,
            size= size,
            total_pages = ceil(total / size)
        )