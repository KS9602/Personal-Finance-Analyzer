from datetime import datetime

from app.core.config import settings
from app.models import Users
from app.models.models import ExpenseCategories, Expenses, DashboardRaport
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

data = [
        {
            "date": "2026-01-12T21:45:51.969571",
            "amount": 134.08
        },
        {
            "date": "2026-01-13T08:19:09.480338",
            "amount": 272.89
        },
        {
            "date": "2026-01-15T08:25:20.200910",
            "amount": 97.01
        },
        {
            "date": "2026-01-19T03:12:47.351637",
            "amount": 174.77
        },
        {
            "date": "2026-01-23T18:54:54.394170",
            "amount": 185.31
        },
        {
            "date": "2026-01-30T11:39:00.433846",
            "amount": 111.61
        },
        {
            "date": "2026-02-04T21:01:25.715037",
            "amount": 154.73
        },
        {
            "date": "2026-02-09T17:44:55.001120",
            "amount": 328.6
        },
        {
            "date": "2026-02-11T23:10:33.309323",
            "amount": 153.91
        },
        {
            "date": "2026-02-15T23:48:41.054930",
            "amount": 395.94
        },
        {
            "date": "2026-02-18T00:00:00",
            "amount": 1000.0
        }
    ]




from sqlalchemy.orm import sessionmaker

class DashboardReportService:

    def __init__(self, session: Session):
        self._session = session


    def get_category_by_id(self, category_id: int) -> str:
        result = self._session.execute(select(ExpenseCategories).where(ExpenseCategories.id == category_id))
        return result.scalar_one_or_none()

    def get_user_by_id(self, user_id):
        return self._session.get(Users,user_id)

    def build_raport(
            self,
            task_id: int,
            raport_uuid: str,
            user_id: int,
            category_id: int,
            date_from: datetime,
            date_to: datetime
    ):
        user = self.get_user_by_id(user_id)
        category = self.get_category_by_id(category_id)
        chart_path = self.create_chart(category, data)
        total_expenses = self.total_expense(user_id)    # TODO DODAC KATEGORIE
        table = self.create_table(user_id, date_from, date_to)
        self.build_pdf(raport_uuid, user, chart_path, total_expenses, table)
        entiti = DashboardRaport(
            task_id = task_id,
            uuid = raport_uuid,
        )
        self._session.add(entiti)
        self._session.commit()
        return entiti

    def total_expense(self, user_id: int):
        result = self._session.execute((select(func.count()).where(Expenses.user_id == user_id)))
        return result.scalar_one()

    def create_table(self, user_id: int, date_from: datetime, date_to: datetime):
        stmt = (select(Expenses)
                .options(selectinload(Expenses.expense_category))
                .where(
            Expenses.user_id == user_id,
            Expenses.date.between(date_from, date_to))
                .order_by(Expenses.date.desc())
            )
        result = self._session.execute(stmt)
        return result.scalars().all()

    def create_chart(self, category, data):
        dates = []
        amounts = []
        for item in data:
            dates.append(item["date"])
            amounts.append(item["amount"])

        plt.figure()
        plt.plot(dates, amounts, marker="o")
        plt.title(f"Expenses ({category.name}) over time")
        plt.xlabel("Date")
        plt.ylabel("Amount")

        plt.xticks(rotation=45)
        id = str(uuid.uuid4())

        path = Path(f"{settings.DASHBOARD_RAPORTS_PATH}/{id}.png")  # todo wywalic do setting
        path.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(path)
        plt.close()

        return path

    def build_table_data(self, expenses: list[Expenses]):
        table_data = [["Date", "Category", "Description", "Amount"]]

        for e in expenses:
            table_data.append([
                e.date.strftime("%Y-%m-%d"),
                e.expense_category.name,
                e.description or "",
                f"{e.amount:.2f}",
            ])

        return table_data
    def build_pdf(self,raport_uuid: str, user, chart_path, total_expenses, table):

        pdf_path = f"{settings.DASHBOARD_RAPORTS_PATH}/{raport_uuid}.pdf"       # todo podmiana

        styles = getSampleStyleSheet()

        elements = []

        elements.append(Paragraph("Expense Report", styles["Title"]))
        elements.append(Spacer(1, 20))

        elements.append(Paragraph(f"User: {user.id}", styles["Normal"]))
        elements.append(Paragraph(f"Total expenses: {total_expenses:.2f} PLN", styles["Normal"]))
        elements.append(Spacer(1, 20))

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
