from app.models.models import ExpenseCategories
from app.repositories.interfaces.IBaseRepository import IBaseRepository


class IExpenseCategoriesRepository(IBaseRepository[ExpenseCategories]):
    ...