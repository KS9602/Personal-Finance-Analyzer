from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Double, UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.models.base import Base
from sqlalchemy import Enum as SQLEnum
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"
    RETRY = "RETRY"


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer,autoincrement=True, primary_key=True, index=True)
    keycloak_id = Column(String(50), unique=True, index=True, nullable=False)

    expenses = relationship("Expenses", back_populates="user", cascade="all, delete-orphan")
    celery_tasks = relationship("CeleryTask", back_populates="user")

class Expenses(Base):
    __tablename__ = "expenses"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("expense_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    description = Column(String(200))
    amount = Column(Double, nullable=False, index=True)

    user = relationship("Users", back_populates="expenses")
    expense_category = relationship("ExpenseCategories", back_populates="expense")


class ExpenseCategories(Base):
    __tablename__ = "expense_categories"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

    expense = relationship("Expenses", back_populates="expense_category", cascade="all, delete-orphan")


class CeleryTask(Base):
    __tablename__ = "celery_task"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    task_id = Column(String(36), nullable=False, unique=True)
    user_id = Column(Integer,ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_type = Column(String(50), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus, name="task_status"),
        default=TaskStatus.PENDING
    )
    einfo = Column(String(4000), nullable=True)

    params = Column(JSONB, nullable=True)

    user = relationship("Users", back_populates="celery_tasks")


class DashboardReport(Base):
    __tablename__ = "dashboard_report"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    task_id = Column(String(36),ForeignKey("celery_task.task_id", ondelete="CASCADE"), nullable=False, index=True)
    uuid = Column(UUID(as_uuid=True), nullable=False)

    task = relationship("CeleryTask")