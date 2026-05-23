from cerebras.cloud.sdk import AsyncCerebras
from app.core.config import settings

class GrammarService:
    def __init__(self):
        self.client = AsyncCerebras(api_key=settings.cerebras_api_key)
        self.model = "llama-3.3-70b"

    async def check_and_reply(self, transcript: str, roleplay: str | None = None, user_context: dict | None = None) -> dict:
        prompt = self._build_prompt(transcript, roleplay, user_context)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
        )
        content = getattr(response.choices[0].message, "content", None) or response.choices[0].message.content
        return self._parse_response(content)

    def _build_prompt(self, transcript: str, roleplay: str | None, user_context: dict | None) -> str:
        role_section = f"You are in a {roleplay} roleplay scenario." if roleplay else "You are a helpful English tutor."
        context_section = "" if not user_context else f"User context: {user_context}."
        return (
            f"{role_section} {context_section}"
            "Analyze the English transcript below. "
            "First extract every grammar or word choice mistake as a JSON array of objects with keys original, correction, explanation. "
            "Then reply naturally to the user, continuing the conversation in an encouraging, fluent tone. "
            "Also provide a follow_up_question to help the student practice more. "
            "Output only valid JSON with keys mistakes, reply, follow_up_question. "
            f"Transcript: \"{transcript}\""
        )

    def _parse_response(self, content: str) -> dict:
        import json

        try:
            payload = json.loads(content)
            return {
                "mistakes": payload.get("mistakes", []),
                "reply": payload.get("reply", ""),
                "follow_up_question": payload.get("follow_up_question", ""),
            }
        except Exception:
            return {
                "mistakes": [],
                "reply": content,
                "follow_up_question": "Can you say that again in a different way?",
            }
