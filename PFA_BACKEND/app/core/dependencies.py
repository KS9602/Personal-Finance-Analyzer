from fastapi import Depends, Request

from app.db.connection import get_db
from app.core.redis_service import RedisService

from app.repositories import (
    UsersRepository,
    ExpensesRepository,
    ExpenseCategoriesRepository
)
from app.services import (
    UsersService,
    ExpensesService,
    ExpenseCategoriesService
)

#REDIS
def get_redis(request: Request):
    return request.app.state.redis

def get_redis_service(redis = Depends(get_redis)):
    return RedisService(redis)



def get_users_repository(db = Depends(get_db)):
    return UsersRepository(db)

def get_users_service(users_repository: UsersRepository = Depends(get_users_repository)):
    return UsersService(users_repository)


def get_expenses_repository(db = Depends(get_db)):
    return ExpensesRepository(db)

def get_expenses_service(expenses_repository: ExpensesRepository = Depends(get_expenses_repository)):
    return ExpensesService(expenses_repository)


def get_expense_categories_repository(db = Depends(get_db)):
    return ExpenseCategoriesRepository(db)

def get_expense_categories_service(expense_categories_repository: ExpenseCategoriesRepository = Depends(get_expense_categories_repository)):
    return ExpenseCategoriesService(expense_categories_repository)

