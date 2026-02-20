from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Double
from sqlalchemy.orm import relationship
from app.models.base import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer,autoincrement=True, primary_key=True, index=True)
    keycloak_id = Column(String(50), unique=True, index=True, nullable=False)

    expense = relationship("Expenses", back_populates="user", cascade="all, delete-orphan")

class Expenses(Base):
    __tablename__ = "expenses"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("expense_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    description = Column(String(200))
    price = Column(Double, nullable=False, index=True)

    user = relationship("Users", back_populates="expenses")
    expense_category = relationship("ExpenseCategories", back_populates="expenses")


class ExpenseCategories(Base):
    __tablename__ = "expense_categories"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

    expense = relationship("Expenses", back_populates="expense", cascade="all, delete-orphan")
