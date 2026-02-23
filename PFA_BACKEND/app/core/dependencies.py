from app.exceptions.exceptions import AuthorizationException
from app.models import Users
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



def get_users_repository(db = Depends(get_db)) -> UsersRepository:
    return UsersRepository(db)

def get_users_service(users_repository: UsersRepository = Depends(get_users_repository)) -> UsersService:
    return UsersService(users_repository)


def get_expenses_repository(db = Depends(get_db)) -> ExpensesRepository:
    return ExpensesRepository(db)

def get_expenses_service(expenses_repository: ExpensesRepository = Depends(get_expenses_repository)) -> ExpensesService:
    return ExpensesService(expenses_repository)


def get_expense_categories_repository(db = Depends(get_db)) -> ExpenseCategoriesRepository:
    return ExpenseCategoriesRepository(db)

def get_expense_categories_service(expense_categories_repository: ExpenseCategoriesRepository = Depends(get_expense_categories_repository))\
        -> ExpenseCategoriesService:
    return ExpenseCategoriesService(expense_categories_repository)


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