import pytest
from datetime import date, datetime

from app.models.models import Expenses
from app.repositories import ExpensesRepository, ExpenseCategoriesRepository
from app.schemas.expense_scheams import ExpenseCreate
from app.services import ExpenseCategoriesService, ExpensesService
from sqlalchemy import select
from tests.base_test_class import BaseTestClass


class TestExpensesService(BaseTestClass):

    @pytest.fixture
    def service(self, db_session) -> ExpensesService:
        repo = ExpensesRepository(db_session)
        category_repo = ExpenseCategoriesRepository(db_session)
        category_service = ExpenseCategoriesService(category_repo)
        return ExpensesService(repo, category_service)


    @pytest.mark.asyncio
    async def test_get_user_expenses_page(self,service, current_user, expenses):
        page = 1
        size = 2

        result = await service.get_user_expenses_page(
            current_user,
            page,
            size
        )
        assert len(result.items) == 2

    @pytest.mark.asyncio
    async def test_get_user_expenses_page_page_not_exist(self,service, current_user, expenses):
        page = 1000
        size = 2

        result = await service.get_user_expenses_page(
            current_user,
            page,
            size
        )
        assert len(result.items) == 0


    @pytest.mark.asyncio
    async def test_add_user_expense(self,service, categories, current_user, db_session):
        amount = 123.12
        description = "ABCD"
        category1, _ = categories
        category_id = category1.id
        command = ExpenseCreate(
            amount = amount,
            description = description,
            category_id = category_id,
            date = datetime.now()
        )
        entity = await service.add_user_expense(current_user, command)
        entity_id = entity.id
        entity_db = await db_session.get(Expenses, entity_id)

        assert entity_db is not None
        assert entity_db.amount == amount
        assert entity_db.description == description
        assert entity_db.category_id == category_id


    @pytest.mark.asyncio
    async def test_delete_expense(self,service, categories, current_user, db_session):
        amount = 123.12
        description = "ABCD"
        category1, _ = categories
        category_id = category1.id
        command = ExpenseCreate(
            amount=amount,
            description=description,
            category_id=category_id,
            date=datetime.now()
        )
        entity = await service.add_user_expense(current_user, command)
        entity_id = entity.id

        await service.delete_expense(current_user, entity_id)

        entity_db = await db_session.get(Expenses, entity_id)
        assert entity_db is None