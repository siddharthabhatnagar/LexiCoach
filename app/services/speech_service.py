import io
import uuid
from deepgram import AsyncDeepgramClient
from app.core.config import settings

class SpeechService:
    def __init__(self):
        self.client = AsyncDeepgramClient(api_key=settings.deepgram_api_key)

    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        try:
            response = await self.client.listen.v1.media.transcribe_file(
                request=audio_bytes,
                model="nova-2",
            )
            channel = response.results.channels[0]
            transcript = channel.alternatives[0].transcript if channel.alternatives else ""
            return transcript.strip()
        except Exception:
            return ""

    async def generate_tts(self, text: str) -> str:
        """Generate TTS audio and return a placeholder URL.
        
        Note: S3 upload removed. For production, configure Firebase Storage
        or another storage provider and upload audio there.
        """
        try:
            response = await self.client.speak.v1.audio.generate(
                text=text,
                voice="aura-asteria-en",
                format="mp3",
            )
            # Return empty string - audio served directly via WebSocket in production
            return ""
        except Exception:
            return ""
