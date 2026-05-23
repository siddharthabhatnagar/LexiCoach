from app.services.vocab_service import VocabService
from app.db.mongo import mongo_db

class DailyVocab:
    def __init__(self):
        self.service = VocabService()

    async def generate_for_user(self, user_id: int, level: str) -> dict:
        return await self.service.generate_daily_vocab(user_id, level)

    async def publish_all_user_vocab(self, users: list[dict]) -> None:
        for user in users:
            await self.service.generate_daily_vocab(user["id"], user.get("cefr_level", "A2"))
