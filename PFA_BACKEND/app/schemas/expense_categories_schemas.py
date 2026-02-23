from pydantic import BaseModel


class ExpenseCategoriesBase(BaseModel):

    id: int
    name: str

    model_config = {"from_attributes": True}
