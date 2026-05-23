from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.dependencies import get_current_user
from app.services.conversation_service import ConversationService
from app.models.user import User

router = APIRouter()
service = ConversationService()

class ConversationRequest(BaseModel):
    transcript: str
    roleplay: str | None = None

class ConversationResponse(BaseModel):
    mistakes: list[dict]
    reply: str
    follow_up_question: str
    audio_url: str

@router.post("/text", response_model=ConversationResponse)
async def text_conversation(request: ConversationRequest, user: User = Depends(get_current_user)):
    if not request.transcript:
        raise HTTPException(status_code=400, detail="Transcript is required")
    response = await service.handle_turn(request.transcript, request.roleplay, connection_id=user.id)
    return response
