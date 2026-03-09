import os.path
from datetime import datetime, date

from app.core.config import settings
from app.models import Users
from app.models.models import ExpenseCategories, Expenses, DashboardReport
from app.schemas.expense_scheams import DashboardDataCommand
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload
import matplotlib.pyplot as plt
import uuid
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

import logging

log = logging.getLogger(__name__)


class DashboardReportService:

    def __init__(self, session: Session):
        self._session = session

    def build_report(
            self,
            task_id: int,
            report_uuid: str,
            cmd: DashboardDataCommand
    ) -> None:

        user = self.get_user_by_id(cmd.user_id)
        chart_path = self.create_chart(cmd)
        total_expenses = self.total_expense(cmd)
        table = self.create_table(cmd)
        self.build_pdf(report_uuid, user, chart_path, total_expenses, table)
        self.save_report_data_db(task_id, report_uuid)



    def get_category_by_id(self, category_id: int) -> ExpenseCategories | None:
        if category_id is None:
            return None
        result = self._session.execute(select(ExpenseCategories).where(ExpenseCategories.id == category_id))
        return result.scalar_one_or_none()

    def get_user_by_id(self, user_id) -> Users | None:
        return self._session.get(Users,user_id)

    def save_report_data_db(self, task_id: int, report_uuid: str) -> None:
        entity = DashboardReport(
            task_id = task_id,
            uuid = report_uuid,
        )
        self._session.add(entity)
        self._session.commit()

    def total_expense(self,cmd: DashboardDataCommand):
        stmt = (
            select(func.sum(Expenses.amount))
            .where(Expenses.user_id == cmd.user_id)
            .where(Expenses.date.between(cmd.date_from, cmd.date_to))
        )
        if cmd.category_id is not None:
            stmt = stmt.where(Expenses.category_id == cmd.category_id)

        result = self._session.execute(stmt)
        total = result.scalar_one()
        return total or 0

    def create_table(self,cmd: DashboardDataCommand) -> list[Expenses]:
        stmt = (select(Expenses)
                .options(selectinload(Expenses.expense_category))
                .where(
            Expenses.user_id == cmd.user_id,
            Expenses.date.between(cmd.date_from, cmd.date_to))
                .order_by(Expenses.date.desc())
            )
        if cmd.category_id is not None:
            stmt = stmt.where(Expenses.category_id == cmd.category_id)

        result = self._session.execute(stmt)
        return result.scalars().all()

    def get_expenses_by_category_and_date(self, cmd: DashboardDataCommand) -> tuple[list[date],list[float]]:
        stmt = (
            select(
                Expenses.date,
                func.sum(Expenses.amount).label("amount")
                )
                .where(Expenses.user_id == cmd.user_id)
                .where(Expenses.date.between(cmd.date_from,cmd.date_to))
                .group_by(Expenses.date)
                .order_by(Expenses.date.asc())
            )
        if cmd.category_id is not None:
            stmt = stmt.where(Expenses.category_id == cmd.category_id)

        result = self._session.execute(stmt)
        data = result.all()

        dates: list[date] = [i.date for i in data]
        amounts: list[float] = [i.amount for i in data]

        return dates, amounts


    def create_chart(self, cmd: DashboardDataCommand) -> Path:
        category = self.get_category_by_id(cmd.category_id)
        dates, amounts = self.get_expenses_by_category_and_date(cmd)

        plt.figure()
        plt.plot(dates, amounts, marker="o")
        plt.title(f"Expenses ({category.name if category else "All categories"}) over time")
        plt.xlabel("Date")
        plt.ylabel("Amount")

        plt.xticks(rotation=45)
        chart_id = str(uuid.uuid4())

        path = Path(f"{settings.DASHBOARD_REPORTS_PATH}/{chart_id}.png")  # todo wywalic do setting
        path.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(path)
        plt.close()

        return path

    def build_table_data(self, expenses: list[Expenses]) -> list[list[str]]:
        table_data = [["Date", "Category", "Description", "Amount"]]

        for e in expenses:
            table_data.append([
                e.date.strftime("%Y-%m-%d"),
                e.expense_category.name,
                e.description or "",
                f"{e.amount:.2f}",
            ])

        return table_data
    def build_pdf(
            self,
            report_uuid: str,
            user: Users,
            chart_path: Path,
            total_expenses: float,
            table: list[Expenses]
    ) -> None:

        pdf_path = f"{settings.DASHBOARD_REPORTS_PATH}/{report_uuid}.pdf"       # todo podmiana

        styles = getSampleStyleSheet()

        elements = []

        elements.append(Paragraph("Expense Report", styles["Title"]))
        elements.append(Spacer(1, 20))

        elements.append(Paragraph(f"User: {user.id}", styles["Normal"]))
        elements.append(Paragraph(f"Total expenses: {total_expenses:.2f} PLN", styles["Normal"]))
        elements.append(Spacer(1, 20))

        if not chart_path.exists():
            raise FileNotFoundError
        elements.append(Image(str(chart_path), width=500, height=300))
        elements.append(Spacer(1, 30))

        table = Table(self.build_table_data(table))

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)

        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
        doc.build(elements)
        return
