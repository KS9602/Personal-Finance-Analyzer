from math import ceil

from app.exceptions.exceptions import AuthorizationException

from app.models.models import Users, Expenses
from app.repositories.expenses_repository import ExpensesRepository
from app.schemas.expense_scheams import ExpenseDataPage, ExpenseCreate

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

    async def add_user_expense_response(self, user: Users, expense_create: ExpenseCreate) -> Expenses:
        expense_entity = Expenses(
            user_id = user.id,
            **expense_create.model_dump()
        )
        return await self.repo.add(expense_entity)


    async def delete_expense(self, user: Users, expense_id: int):
        expense_entity = await self.repo.get_by_id(expense_id)
        if not expense_entity or expense_entity.user_id != user.id:
            raise AuthorizationException(403)
        await self.repo.delete_by_id(expense_id)