from datetime import datetime, timedelta
from typing import List
from app.db.mongo import mongo_db
from cerebras.cloud.sdk import AsyncCerebras
from app.core.config import settings

class VocabService:
    def __init__(self):
        self.client = AsyncCerebras(api_key=settings.cerebras_api_key)
        self.model = "llama-3.3-70b"

    async def generate_daily_vocab(self, user_id: int, level: str) -> dict:
        prompt = (
            f"Create 5 English vocabulary words for a CEFR level {level} learner. "
            "Return JSON with keys words where each item includes word, definition, example, mnemonic. "
            "Make examples contextual for speaking practice."
        )
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )
        content = getattr(response.choices[0].message, "content", None) or response.choices[0].message.content
        vocab_list = self._parse_vocab_response(content)
        payload = {
            "user_id": user_id,
            "level": level,
            "words": vocab_list,
            "generated_at": datetime.utcnow(),
        }
        await mongo_db.vocab.replace_one({"user_id": user_id}, payload, upsert=True)
        return payload

    def _parse_vocab_response(self, content: str) -> List[dict]:
        import json

        try:
            data = json.loads(content)
            return data.get("words", [])
        except Exception:
            return []

    async def get_daily_vocab(self, user_id: int) -> dict | None:
        return await mongo_db.vocab.find_one({"user_id": user_id})

    async def add_spaced_repetition_card(self, user_id: int, word: str, definition: str, example: str) -> dict:
        item = {
            "user_id": user_id,
            "word": word,
            "definition": definition,
            "example": example,
            "ease_factor": 2.5,
            "interval_days": 1,
            "repetitions": 0,
            "next_review": datetime.utcnow(),
            "history": [],
        }
        await mongo_db.spaced_repetition.insert_one(item)
        return item

    async def get_due_cards(self, user_id: int) -> list[dict]:
        now = datetime.utcnow()
        cursor = mongo_db.spaced_repetition.find({"user_id": user_id, "next_review": {"$lte": now}})
        return await cursor.to_list(length=50)

    async def record_review(self, card_id, quality: int) -> dict | None:
        card = await mongo_db.spaced_repetition.find_one({"_id": card_id})
        if not card:
            return None
        ease = card.get("ease_factor", 2.5)
        interval = card.get("interval_days", 1)
        reps = card.get("repetitions", 0) + 1
        ease = max(1.3, ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        if quality < 3:
            interval = 1
        elif reps == 1:
            interval = 1
        elif reps == 2:
            interval = 6
        else:
            interval = int(interval * ease)
        next_review = datetime.utcnow() + timedelta(days=interval)
        update = {
            "$set": {
                "ease_factor": ease,
                "interval_days": interval,
                "next_review": next_review,
                "repetitions": reps,
            },
            "$push": {
                "history": {"reviewed_at": datetime.utcnow(), "quality": quality, "interval": interval},
            },
        }
        await mongo_db.spaced_repetition.update_one({"_id": card_id}, update)
        return await mongo_db.spaced_repetition.find_one({"_id": card_id})
