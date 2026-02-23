from datetime import datetime
from typing import List

from pydantic import BaseModel

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
