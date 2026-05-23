import io
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.db.mongo import mongo_db

class WeeklyReport:
    async def generate_for_user(self, user_id: int) -> bytes:
        last_week = datetime.utcnow() - timedelta(days=7)
        history = await mongo_db.chat_history.find({"user_id": user_id, "created_at": {"$gte": last_week}}).to_list(length=200)
        mistakes = sum(len(item.get("mistakes", [])) for item in history)
        sessions = len(history)
        pdf_buffer = io.BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
        pdf.setTitle("Weekly English Progress Report")
        pdf.drawString(72, 720, f"Weekly Progress Report")
        pdf.drawString(72, 700, f"User ID: {user_id}")
        pdf.drawString(72, 680, f"Date: {datetime.utcnow().strftime('%Y-%m-%d')}")
        pdf.drawString(72, 640, f"Sessions Reviewed: {sessions}")
        pdf.drawString(72, 620, f"Total Grammar Mistakes: {mistakes}")
        mistake_rate = round(mistakes / sessions, 3) if sessions else 0.0
        pdf.drawString(72, 600, f"Average Mistake Rate: {mistake_rate}")
        pdf.drawString(72, 560, "Summary:")
        pdf.drawString(72, 540, "Keep practicing daily, focus on accuracy, and review vocabulary cards.")
        pdf.showPage()
        pdf.save()
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    async def save_report(self, user_id: int, pdf_data: bytes) -> None:
        await mongo_db.weekly_reports.update_one(
            {"user_id": user_id},
            {"$set": {"generated_at": datetime.utcnow(), "report_pdf": pdf_data}},
            upsert=True,
        )
