from app.auth.auth_api_route import AuthApiRouter
from app.schemas.expense_categories_schemas import ExpenseCategoriesBase
from fastapi import Query
import logging

from app.schemas.expense_scheams import ExpenseDataPage, ExpenseCreate, ExpenseBase
from app.auth.utils_auth import authenticated
from app.core.dependencies import CurrentUserDP, ExpensesDP, ExpensesCategoriesDP


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



@router.get("/get_expense_categories", response_model=list[ExpenseCategoriesBase])
@authenticated
async def get_expense_categories(
        expense_categories_service : ExpensesCategoriesDP
):
    return await expense_categories_service.repo.get_all()



@router.post("/add_expense", response_model=ExpenseBase)
@authenticated
async def add_expense(
        new_expense: ExpenseCreate,
        user: CurrentUserDP,
        expense_service: ExpensesDP
):
    return await expense_service.add_user_expense_response(user, new_expense)

@router.delete("/delete_expense/{expense_id}", status_code=204)
@authenticated
async def delete_expense(
        expense_id: int,
        user: CurrentUserDP,
        expense_serivce: ExpensesDP
):
    await expense_serivce.delete_expense(user, expense_id)
