from app.services.vocab_service import VocabService

class DailyVocab:
    def __init__(self):
        self.service = VocabService()

    async def generate_for_user(self, email: str, level: str) -> dict:
        return await self.service.generate_daily_vocab(email, level)

    async def publish_all_user_vocab(self, users: list[dict]) -> None:
        for user in users:
            await self.service.generate_daily_vocab(user["email"], user.get("cefr_level", "A2"))
