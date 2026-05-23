from celery import shared_task
import asyncio
from sqlalchemy import select
from app.services.vocab_service import VocabService
from app.db.postgres import async_session
from app.models.user import User

@shared_task(name="app.modules.daily_vocab_task.generate_daily_vocab_for_users")
def generate_daily_vocab_for_users():
    vocab_service = VocabService()

    async def _run():
        async with async_session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            for user in users:
                await vocab_service.generate_daily_vocab(user.id, user.cefr_level or "A2")

    asyncio.run(_run())
