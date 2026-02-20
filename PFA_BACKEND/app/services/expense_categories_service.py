from app.repositories.expense_categories_repository import ExpenseCategoriesRepository
import logging

log = logging.getLogger(__name__)

class ExpenseCategoriesService:
    def __init__(self,repo: ExpenseCategoriesRepository):
        self.repo = repo