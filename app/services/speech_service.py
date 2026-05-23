import io
import uuid
import aioboto3
from deepgram import AsyncDeepgramClient
from app.core.config import settings

class SpeechService:
    def __init__(self):
        self.client = AsyncDeepgramClient(api_key=settings.deepgram_api_key)

    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        response = await self.client.listen.v1.media.transcribe_file(
            request=audio_bytes,
            model="nova-2",
        )
        channel = response.results.channels[0]
        transcript = channel.alternatives[0].transcript if channel.alternatives else ""
        return transcript.strip()

    async def generate_tts(self, text: str) -> str:
        response = await self.client.speak.v1.audio.generate(
            text=text,
            voice="aura-asteria-en",
            format="mp3",
        )
        audio_body = response.stream.read() if hasattr(response, "stream") else response
        if isinstance(audio_body, bytes):
            data = audio_body
        elif hasattr(audio_body, "getvalue"):
            data = audio_body.getvalue()
        else:
            data = bytes(audio_body)
        filename = f"tts/{uuid.uuid4().hex}.mp3"
        url = await self._upload_to_s3(filename, data)
        return url

    async def _upload_to_s3(self, key: str, data: bytes) -> str:
        session = aioboto3.Session(
            aws_access_key_id=settings.aws_access_key,
            aws_secret_access_key=settings.aws_secret_key,
            region_name=settings.aws_region,
        )
        async with session.client("s3") as s3:
            await s3.put_object(Bucket=settings.aws_bucket, Key=key, Body=data, ContentType="audio/mpeg")
            url = await s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": settings.aws_bucket, "Key": key},
                ExpiresIn=3600,
            )
            return url
