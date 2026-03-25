from datetime import datetime

import pytest
from app.models import Users
from app.models.models import ExpenseCategories, Expenses


class BaseTestClass:
    @pytest.fixture()
    async def current_user(self, db_session):
        user = await db_session.get(Users,1)
        await db_session.refresh(user)
        return user


    @pytest.fixture
    async def categories(self, db_session):
        category1 = ExpenseCategories(id=100, name="Test1")
        category2 = ExpenseCategories(id=101, name="Test2")

        db_session.add_all([category1, category2])
        await db_session.flush()

        return category1, category2

    @pytest.fixture
    async def expenses(self, db_session, current_user, categories):
        category1, category2 = categories
        expenses = [
            Expenses(id=1000,user_id=current_user.id, category_id=category1.id,description="Wydatek 1", date=datetime.now(), amount=10.5),
            Expenses(id=1001,user_id=current_user.id, category_id=category1.id,description="Wydatek 2", date=datetime.now(), amount=15.5),
            Expenses(id=1002,user_id=current_user.id, category_id=category2.id,description="Wydatek 3", date=datetime.now(), amount=105.5),
        ]

        db_session.add_all(expenses)
        await db_session.flush()

        return expenses
