import io
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.db.firebase import get_firestore_db

class WeeklyReport:
    async def generate_for_user(self, email: str) -> bytes:
        db = get_firestore_db()
        last_week = datetime.utcnow() - timedelta(days=7)

        history_docs = (
            db.collection("chat_history")
            .where("email", "==", email)
            .where("created_at", ">=", last_week)
            .limit(200)
            .stream()
        )
        history = [doc.to_dict() for doc in history_docs]

        mistakes = sum(len(item.get("mistakes", [])) for item in history)
        sessions = len(history)

        pdf_buffer = io.BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
        pdf.setTitle("Weekly English Progress Report")
        pdf.drawString(72, 720, "Weekly Progress Report")
        pdf.drawString(72, 700, f"User: {email}")
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

    async def save_report(self, email: str, pdf_data: bytes) -> None:
        db = get_firestore_db()
        db.collection("weekly_reports").document(email).set({
            "email": email,
            "generated_at": datetime.utcnow(),
            # Note: storing raw PDF bytes in Firestore is not recommended for large files.
            # For production, upload to Firebase Storage and store the URL instead.
            "report_size_bytes": len(pdf_data),
        }, merge=True)
