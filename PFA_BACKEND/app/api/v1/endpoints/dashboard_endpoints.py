from app.auth.auth_api_route import AuthApiRouter
from app.models import Users
from fastapi import Query, Depends
import logging

from app.schemas.expense_scheams import ExpenseDataPage, ExpenseCreate
from app.auth.utils_auth import authenticated
from app.services import ExpensesService
from app.core.dependencies import get_expenses_service, get_current_user, CurrentUserDP, RedisDP, ExpensesDP

log = logging.getLogger(__name__)

router = AuthApiRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/get_expenses_page", response_model=ExpenseDataPage)
@authenticated
async def get_expenses_page(
        user: CurrentUserDP,
        expense_service: ExpensesDP,
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=10),

):
    return  await expense_service.get_user_expenses_page(user,page,size)


@router.post("/add_expense")
@authenticated
async def add_expense(
        user: CurrentUserDP,
        expense_service: ExpensesDP,
        new_expense: ExpenseCreate,
):

    pass