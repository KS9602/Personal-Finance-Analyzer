from datetime import datetime, date, timedelta
from typing import List

from pydantic import BaseModel, model_validator

class ExpenseBase(BaseModel):
    id: int
    amount: float
    description: str
    category_id : int
    date: datetime

    model_config = {"from_attributes": True}


class CategoryOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ExpenseOut(BaseModel):
    id: int
    amount: float
    description: str
    expense_category: CategoryOut
    date: datetime

    model_config = {"from_attributes": True}


class ExpenseDataPage(BaseModel):
    items: List[ExpenseOut]
    total: int
    page: int
    size: int
    total_pages: int

class ExpenseCreate(BaseModel):
    amount: float
    description: str
    category_id: int
    date: datetime


class ExpenseScope(BaseModel):
    date_scope_start: datetime
    date_scope_end: datetime
    category: int | None

    @model_validator(mode="after")
    def date_validator(self):
        if self.date_scope_start > self.date_scope_end:
            raise ValueError("Start date is latest than end date")
        return self

class ExpenseCharData(BaseModel):
    date: datetime
    amount: float


class DashboardChartResponse(BaseModel):
    data: List[ExpenseCharData]


class ReportGenerateResponse(BaseModel):
    report_uuid: str

class DashboardDataCommand(BaseModel):
    user_id: int
    category_id: int | None
    date_from: date
    date_to: date

    @model_validator(mode="after")
    def valid_chart_dates(self):
        if self.date_from > self.date_to:
            raise ValueError("Start date is latest than end date")
        if self.date_to is None:
            self.date_to = datetime.now()
        if self.date_from is None:
            self.date_from = self.date_to - timedelta(weeks=8)


