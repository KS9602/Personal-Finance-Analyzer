from datetime import  datetime

import pytest
from app.models.models import ExpenseCategories, Users, Expenses
from asyncpg.pgproto.pgproto import timedelta
from sqlalchemy import select, func
from tests.base_test_class import BaseTestClass
from tests.conftest import client

class TestDashboard(BaseTestClass):


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



    @pytest.mark.asyncio
    async def test_user_chart(self, client, expenses, categories):
        date_from = (datetime.now() - timedelta(days=1)).date()
        date_to = (datetime.now() + timedelta(hours=1)).date()
        category, _ = categories

        respone = await client.get(
            url="/api/v1/dashboard/user_chart",
            params={
                "category_id": category.id,
                "date_from": date_from,
                "date_to": date_to
            }
        )
        data = respone.json()

        assert respone.status_code == 200
        assert len(data.get("data")) == 2


    @pytest.mark.asyncio
    async def test_user_chart_all_categories(self, client, expenses):
        date_from = (datetime.now() - timedelta(days=1)).date()
        date_to = (datetime.now() + timedelta(hours=1)).date()

        respone = await client.get(
            url="/api/v1/dashboard/user_chart",
            params={
                "date_from": date_from,
                "date_to": date_to
            }
        )
        data = respone.json()

        assert respone.status_code == 200
        assert len(data.get("data")) == 3


