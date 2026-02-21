from datetime import datetime
from typing import List

from pydantic import BaseModel


class ExpenseOut(BaseModel):
    id: int
    price: float
    description: str
    date: datetime

    model_config = {"from_attributes": True}


class ExpenseDataPage(BaseModel):
    items: List[ExpenseOut]
    total: int
    page: int
    size: int
    total_pages: int

