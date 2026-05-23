from datetime import datetime
from app.services.speech_service import SpeechService
from app.services.grammar_service import GrammarService
from app.services.vocab_service import VocabService
from app.db.firebase import get_firestore_db
from app.db.redis_client import redis_client
from app.modules.roleplay import ROLEPLAY_PROMPTS

class ConversationService:
    def __init__(self):
        self.speech = SpeechService()
        self.grammar = GrammarService()
        self.vocab = VocabService()

    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        return await self.speech.transcribe_audio(audio_bytes)

    async def handle_turn(self, transcript: str, roleplay: str | None, connection_id: int, email: str | None = None) -> dict:
        context = await self._fetch_session_context(connection_id)
        roleplay_name = roleplay or context.get("roleplay")
        user_context = {"session": context}
        grammar_response = await self.grammar.check_and_reply(transcript, roleplay_name, user_context)
        audio_url = await self.speech.generate_tts(grammar_response["reply"])
        await self._save_conversation(connection_id, transcript, grammar_response, email)
        await self._update_streak(connection_id, grammar_response, email)
        return {
            "mistakes": grammar_response["mistakes"],
            "reply": grammar_response["reply"],
            "follow_up_question": grammar_response["follow_up_question"],
            "audio_url": audio_url,
        }

    async def _fetch_session_context(self, connection_id: int) -> dict:
        raw = await redis_client.get(f"session:{connection_id}")
        if raw:
            import json
            return json.loads(raw)
        return {"roleplay": None, "created_at": datetime.utcnow().isoformat()}

    async def _save_conversation(self, connection_id: int, transcript: str, grammar_response: dict, email: str | None = None) -> None:
        now = datetime.utcnow()
        db = get_firestore_db()
        db.collection("chat_history").add({
            "session_id": connection_id,
            "email": email,
            "transcript": transcript,
            "mistakes": grammar_response["mistakes"],
            "reply": grammar_response["reply"],
            "follow_up_question": grammar_response["follow_up_question"],
            "created_at": now,
        })

    async def _update_streak(self, connection_id: int, grammar_response: dict, email: str | None = None) -> None:
        key = f"streak:{email or connection_id}"
        streak = await redis_client.get(key)
        streak = int(streak or 0)
        streak += 1 if grammar_response["mistakes"] else 0
        await redis_client.set(key, streak, ex=86400)
