from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.dependencies import get_current_user
from app.services.vocab_service import VocabService
from app.services.user_service import User

router = APIRouter()
service = VocabService()

class VocabRequest(BaseModel):
    level: str

@router.post("/daily")
async def generate_daily_vocab(request: VocabRequest, user: User = Depends(get_current_user)):
    vocab = await service.generate_daily_vocab(user.email, request.level)
    return vocab

@router.get("/daily")
async def get_daily_vocab(user: User = Depends(get_current_user)):
    vocab = await service.get_daily_vocab(user.email)
    return vocab or {}

@router.post("/review")
async def review_card(card_id: str, quality: int, user: User = Depends(get_current_user)):
    card = await service.record_review(card_id, quality)
    return {"card": card}
