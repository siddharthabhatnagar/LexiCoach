from celery import shared_task
import asyncio
from app.modules.weekly_report import WeeklyReport
from app.db.firebase import get_firestore_db

@shared_task(name="app.modules.weekly_report_task.generate_weekly_reports")
def generate_weekly_reports():
    report = WeeklyReport()

    async def _run():
        db = get_firestore_db()
        users_docs = db.collection("users").stream()
        for doc in users_docs:
            user = doc.to_dict()
            email = user.get("email")
            if email:
                pdf_bytes = await report.generate_for_user(email)
                await report.save_report(email, pdf_bytes)

    asyncio.run(_run())
