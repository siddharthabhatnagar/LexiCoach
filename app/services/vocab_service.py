from datetime import datetime, timedelta
from typing import List
from cerebras.cloud.sdk import AsyncCerebras
from app.core.config import settings
from app.db.firebase import get_firestore_db
import logging
import uuid

class VocabService:
    def __init__(self):
        self.client = AsyncCerebras(api_key=settings.cerebras_api_key)
        self.model = "llama-3.3-70b"

    async def generate_daily_vocab(self, email: str, level: str) -> dict:
        prompt = (
            f"Create 5 English vocabulary words for a CEFR level {level} learner. "
            "Return JSON with keys words where each item includes word, definition, example, mnemonic. "
            "Make examples contextual for speaking practice."
        )
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
            )
            content = getattr(response.choices[0].message, "content", None) or response.choices[0].message.content
            vocab_list = self._parse_vocab_response(content)
        except Exception as e:
            logging.error(f"Error generating vocab from Cerebras: {e}")
            vocab_list = []

        payload = {
            "email": email,
            "level": level,
            "words": vocab_list,
            "generated_at": datetime.utcnow(),
        }
        db = get_firestore_db()
        db.collection("vocab").document(email).set(payload)
        return payload

    def _parse_vocab_response(self, content: str) -> List[dict]:
        import json
        try:
            # simple extraction for json inside markdown block if any
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            data = json.loads(content)
            return data.get("words", [])
        except Exception:
            return []

    async def get_daily_vocab(self, email: str) -> dict | None:
        db = get_firestore_db()
        doc = db.collection("vocab").document(email).get()
        if doc.exists:
            return doc.to_dict()
        return None

    async def add_spaced_repetition_card(self, email: str, word: str, definition: str, example: str) -> dict:
        card_id = str(uuid.uuid4())
        item = {
            "id": card_id,
            "email": email,
            "word": word,
            "definition": definition,
            "example": example,
            "ease_factor": 2.5,
            "interval_days": 1,
            "repetitions": 0,
            "next_review": datetime.utcnow(),
            "history": [],
        }
        db = get_firestore_db()
        db.collection("spaced_repetition").document(card_id).set(item)
        return item

    async def get_due_cards(self, email: str) -> list[dict]:
        db = get_firestore_db()
        now = datetime.utcnow()
        docs = db.collection("spaced_repetition").where("email", "==", email).where("next_review", "<=", now).limit(50).stream()
        return [doc.to_dict() for doc in docs]

    async def record_review(self, card_id: str, quality: int) -> dict | None:
        db = get_firestore_db()
        card_ref = db.collection("spaced_repetition").document(card_id)
        doc = card_ref.get()
        if not doc.exists:
            return None
        card = doc.to_dict()
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
        
        history = card.get("history", [])
        history.append({"reviewed_at": datetime.utcnow(), "quality": quality, "interval": interval})
        
        update = {
            "ease_factor": ease,
            "interval_days": interval,
            "next_review": next_review,
            "repetitions": reps,
            "history": history
        }
        card_ref.update(update)
        updated_doc = card_ref.get()
        return updated_doc.to_dict()
