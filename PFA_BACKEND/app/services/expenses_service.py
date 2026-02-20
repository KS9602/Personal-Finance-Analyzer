from app.repositories.expenses_repository import ExpensesRepository
import logging

log = logging.getLogger(__name__)

class ExpensesService:
    def __init__(self,repo: ExpensesRepository):
        self.repo = repo