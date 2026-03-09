from app.repositories.interfaces.IExpenseCategoriesRepository import IExpenseCategoriesRepository

import logging

log = logging.getLogger(__name__)

class ExpenseCategoriesService:
    def __init__(self,repo: IExpenseCategoriesRepository):
        self.repo = repo