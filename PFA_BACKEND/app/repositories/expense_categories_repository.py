from app.repositories.base_repository import BaseRepository
from app.models.models import ExpenseCategories

class ExpenseCategoriesRepository(BaseRepository[ExpenseCategories]):
    model = ExpenseCategories
