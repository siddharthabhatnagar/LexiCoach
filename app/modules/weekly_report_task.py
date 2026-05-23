from celery import shared_task
import asyncio
from sqlalchemy import select
from app.modules.weekly_report import WeeklyReport
from app.db.postgres import async_session
from app.models.user import User

@shared_task(name="app.modules.weekly_report_task.generate_weekly_reports")
def generate_weekly_reports():
    report = WeeklyReport()

    async def _run():
        async with async_session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            for user in users:
                pdf_bytes = await report.generate_for_user(user.id)
                await report.save_report(user.id, pdf_bytes)

    asyncio.run(_run())
