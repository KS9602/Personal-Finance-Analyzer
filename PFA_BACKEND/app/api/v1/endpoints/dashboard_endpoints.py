from datetime import date
from typing import Optional
from starlette.responses import FileResponse

from fastapi import Query
import logging
from app.auth.auth_api_route import AuthApiRouter
from app.schemas.expense_categories_schemas import ExpenseCategoriesBase
from app.auth.utils_auth import authenticated
from app.core.dependencies import CurrentUserDP, ExpensesDP, ExpensesCategoriesDP
from app.schemas.expense_scheams import (
    ExpenseDataPage,
    ExpenseCreate,
    ExpenseBase,
    DashboardChartResponse,
    ReportGenerateResponse,
    DashboardDataCommand
)


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
    return await expense_service.add_user_expense(user, new_expense)

@router.delete("/delete_expense/{expense_id}", status_code=204)
@authenticated
async def delete_expense(
        expense_id: int,
        user: CurrentUserDP,
        expense_serivce: ExpensesDP
):
    await expense_serivce.delete_expense(user, expense_id)


@router.get("/user_chart", response_model=DashboardChartResponse)
@authenticated
async def dashboard_user_chart(
        user: CurrentUserDP,
        expense_serivce: ExpensesDP,
        category_id: Optional[int] = Query(None),
        date_from: Optional[date] = Query(...),
        date_to: Optional[date] = Query(...),
):
    command = DashboardDataCommand(
        user_id=user.id,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to
    )
    return await expense_serivce.expense_chart(command)

@router.get("/generate_report", response_model=ReportGenerateResponse)
@authenticated
async def generate_report(
        user: CurrentUserDP,
        expense_serivce: ExpensesDP,
        category_id: Optional[int] = Query(None),
        date_from: Optional[date] = Query(...),
        date_to: Optional[date] = Query(...)
):
    command = DashboardDataCommand(
        user_id=user.id,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to
    )
    return await expense_serivce.delay_report_generate(command)

@router.get("/download_dashboard_report", response_class=FileResponse)
@authenticated
async def download_dashboard_report(
        user: CurrentUserDP,
        expense_serivce: ExpensesDP,
        report_uuid: Optional[str] = Query(...),
):
    return await expense_serivce.download_report(user, report_uuid)
