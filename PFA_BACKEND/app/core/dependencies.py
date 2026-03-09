from app.exceptions.exceptions import AuthorizationException
from app.models import Users
from app.repositories.interfaces.IExpenseCategoriesRepository import IExpenseCategoriesRepository
from app.repositories.interfaces.IExpensesRepository import IExpenseRepository
from app.repositories.interfaces.IUsersRepository import IUsersRepository
from fastapi import Depends, Request
from typing import Annotated
from redis.asyncio import Redis

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
def get_redis(request: Request) -> Redis:
    return request.app.state.redis

def get_redis_service(redis = Depends(get_redis)) -> RedisService:
    return RedisService(redis)



def get_users_repository(db = Depends(get_db)) -> IUsersRepository:
    return UsersRepository(db)

def get_users_service(users_repository: IUsersRepository = Depends(get_users_repository)) -> UsersService:
    return UsersService(users_repository)

def get_expense_categories_repository(db = Depends(get_db)) -> IExpenseCategoriesRepository:
    return ExpenseCategoriesRepository(db)

def get_expense_categories_service(expense_categories_repository: IExpenseCategoriesRepository = Depends(get_expense_categories_repository))\
        -> ExpenseCategoriesService:
    return ExpenseCategoriesService(expense_categories_repository)



def get_expenses_repository(db = Depends(get_db)) -> IExpenseRepository:
    return ExpensesRepository(db)

def get_expenses_service(
        expenses_repository: IExpenseRepository = Depends(get_expenses_repository),
        expense_categories_service: ExpenseCategoriesService = Depends(get_expense_categories_service)
                         ) -> ExpensesService:
    return ExpensesService(expenses_repository, expense_categories_service)



async def get_current_user(
    request: Request,
    users_service: UsersService = Depends(get_users_service),
) -> Users:
    sub = request.state.sub
    if not sub:
        raise AuthorizationException(401)

    user = await users_service.get_user_by_kc_id(sub)

    if not user:
        raise AuthorizationException(401)

    return user


CurrentUserDP = Annotated[Users, Depends(get_current_user)]
RedisDP = Annotated[RedisService, Depends(get_redis_service)]
ExpensesDP = Annotated[ExpensesService, Depends(get_expenses_service)]
ExpensesCategoriesDP = Annotated[ExpenseCategoriesService, Depends(get_expense_categories_service)]