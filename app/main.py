import os
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.routes.auth import router as auth_router
from app.routes.conversation import router as conversation_router
from app.routes.vocab import router as vocab_router
from app.routes.progress import router as progress_router
from app.services.conversation_service import ConversationService
from app.core.auth import decode_access_token
from app.services.user_service import UserService
from app.core.dependencies import get_redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("english_app")

app = FastAPI(title="LexiCoach English AI Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(conversation_router, prefix="/conversation", tags=["conversation"])
app.include_router(vocab_router, prefix="/vocab", tags=["vocab"])
app.include_router(progress_router, prefix="/progress", tags=["progress"])

@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Starting LexiCoach backend")
    await get_redis()

@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("Shutting down LexiCoach backend")

@app.websocket("/ws/audio")
async def websocket_audio(websocket: WebSocket):
    await websocket.accept()
    service = ConversationService()
    audio_buffer = bytearray()
    roleplay = None
    user_id = None
    try:
        token = websocket.query_params.get("token")
        if token:
            payload = decode_access_token(token)
            if payload:
                user = await UserService.get_by_email(payload.get("sub"))
                user_id = user.id if user else None
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.receive_text":
                payload = message.get("text")
                if payload:
                    text = payload.strip()
                    if text.startswith("{"):
                        import json
                        data = json.loads(text)
                        roleplay = data.get("roleplay") or roleplay
                        if data.get("event") == "flush":
                            audio_buffer = bytearray()
                            await websocket.send_json({"status": "ready"})
                            continue
            elif message["type"] == "websocket.receive_bytes":
                audio_buffer.extend(message["bytes"])
                if len(audio_buffer) < 4096:
                    continue
                transcript = await service.transcribe_audio(bytes(audio_buffer))
                response = await service.handle_turn(
                    transcript=transcript,
                    roleplay=roleplay,
                    connection_id=id(websocket),
                    user_id=user_id,
                )
                await websocket.send_json(response)
                audio_buffer = bytearray()
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception:
        logger.exception("WebSocket error")
        await websocket.close(code=1011)

@app.get("/healthz")
async def healthcheck():
    return JSONResponse({"status": "ok", "service": "english_app"})
