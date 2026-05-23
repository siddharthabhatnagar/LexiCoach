from celery import shared_task
import asyncio
from app.services.vocab_service import VocabService
from app.db.firebase import get_firestore_db

@shared_task(name="app.modules.daily_vocab_task.generate_daily_vocab_for_users")
def generate_daily_vocab_for_users():
    vocab_service = VocabService()

    async def _run():
        db = get_firestore_db()
        users_docs = db.collection("users").stream()
        for doc in users_docs:
            user = doc.to_dict()
            email = user.get("email")
            level = user.get("cefr_level", "A2")
            if email:
                await vocab_service.generate_daily_vocab(email, level)

    asyncio.run(_run())
