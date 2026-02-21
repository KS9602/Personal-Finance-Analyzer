from app.auth.auth_api_route import AuthApiRouter
from fastapi import Query, Request, Depends
import logging

from app.schemas.schemas import ExpenseDataPage
from app.auth.utils_auth import authenticated
from app.services import ExpensesService, UsersService
from app.core.dependencies import get_expenses_service, get_users_service

log = logging.getLogger(__name__)

router = AuthApiRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/get_expenses", response_model=ExpenseDataPage)
@authenticated
async def get_expenses(
        request: Request,
        expenses_service: ExpensesService = Depends(get_expenses_service),
        users_service: UsersService = Depends(get_users_service),
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=10),

):
    user = await users_service.get_user_by_kc_id(request.state.sub)
    response = await expenses_service.get_user_expenses_page(
        user,
        page,
        size
    )

    return response