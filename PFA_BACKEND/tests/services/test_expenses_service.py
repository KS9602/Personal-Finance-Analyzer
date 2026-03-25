import pytest
from app.repositories import ExpensesRepository, ExpenseCategoriesRepository
from app.services import ExpenseCategoriesService, ExpensesService
from tests.base_test_class import BaseTestClass


class TestExpensesService(BaseTestClass):

    @pytest.fixture
    def service(self, db_session) -> ExpensesService:
        repo = ExpensesRepository(db_session)
        category_repo = ExpenseCategoriesRepository(db_session)
        category_service = ExpenseCategoriesService(category_repo)
        return ExpensesService(repo, category_service)

