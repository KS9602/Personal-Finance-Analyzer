import matplotlib.pyplot as plt
import uuid
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

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




def create_chart(category, data):
    dates = []
    amounts = []
    for item in data:
        dates.append(item["date"])
        amounts.append(item["amount"])

    plt.figure()
    plt.plot(dates, amounts, marker="o")
    plt.title(f"Expenses ({category}) over time")
    plt.xlabel("Date")
    plt.ylabel("Amount")

    plt.xticks(rotation=45)
    id = str(uuid.uuid4())

    path = Path(f"raports/charts/{id}.png")      # todo wywalic do setting
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path


def build_pdf(user_data, category_id, chart_data, table_data):

    chart_path = create_chart(category_id, chart_data)

    pdf_id = str(uuid.uuid4())
    pdf_path = Path("raports/pdfs") / f"{pdf_id}.pdf"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("Expense Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(Image(str(chart_path), width=500, height=300))
    elements.append(Spacer(1, 30))
    table_data = [
        ["Date", "Amount"],
        ["2026-01-12", "134.08"],
        ["2026-01-13", "272.89"],
        ["2026-01-15", "97.01"],
    ]

    table = Table(table_data)

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ])
    )

    elements.append(table)

    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    doc.build(elements)

    return pdf_path

