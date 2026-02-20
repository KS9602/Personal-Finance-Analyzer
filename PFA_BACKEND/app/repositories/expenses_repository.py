from app.repositories.base_repository import BaseRepository
from app.models.models import Expenses

class ExpensesRepository(BaseRepository[Expenses]):
    model = Expenses
