from datetime import  datetime

import pytest
from app.models.models import ExpenseCategories, Users, Expenses
from sqlalchemy import select, func
from tests.conftest import client

class TestDashboard:

    @pytest.fixture()
    async def current_user(self, db_session):
        user = await db_session.get(Users,1)
        await db_session.refresh(user)
        return user


    @pytest.fixture
    async def categories(self, db_session):
        category1 = ExpenseCategories(name="Test1")
        category2 = ExpenseCategories(name="Test2")

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


    @pytest.mark.asyncio
    async def test_get_expenses_page(self, client, expenses, categories):
        response = await client.get(
            url="/api/v1/dashboard/get_expenses_page",
            params={"page": 1, "size": 2}
        )
        data = response.json()

        assert response.status_code == 200
        assert len(data.get("items")) == 2
        assert data.get("size") == len(data.get("items"))
        assert data.get("total") == 3


    @pytest.mark.asyncio
    async def test_create_expense(self, client, categories):

        response = await client.get("/api/v1/dashboard/get_expense_categories")

        assert response.status_code == 200
        assert len(response.json()) == 2


    @pytest.mark.asyncio
    async def test_add_expense(self, client, categories, current_user):
        category1, category2 = categories
        category_id = category1.id
        payload = {
            "category_id": category_id,
            "amount": 99.9,
            "description":"kolejny wydatek",
            "date": datetime.now().isoformat()
        }

        response = await client.post(
            url="/api/v1/dashboard/add_expense",
            json=payload
        )
        data = response.json()


        assert response.status_code == 200
        assert data.get("amount") == 99.9
        assert data.get("category_id") == category_id


    @pytest.mark.asyncio
    async def test_delete_expense(self, client, expenses, db_session):
        expense_id = 1000

        result = await db_session.execute(select(func.count()).select_from(Expenses))
        expenses_count_before = result.scalar()

        response = await client.delete(
            url=f"/api/v1/dashboard/delete_expense/{expense_id}"
        )

        result = await db_session.execute(select(func.count()).select_from(Expenses))
        expenses_count_after = result.scalar()

        assert expenses_count_before - 1 == expenses_count_after
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_expense_not_exists(self, client):
        expense_id = 5555
        response = await client.delete(
            url=f"/api/v1/dashboard/delete_expense/{expense_id}"
        )
        assert response.status_code == 307


    #
    # @pytest.mark.asyncio
    # async def test_user_chart(self, client):