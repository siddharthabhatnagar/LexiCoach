from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.models.user import User
from app.db.mongo import mongo_db

router = APIRouter()

@router.get("/stats")
async def progress_stats(user: User = Depends(get_current_user)):
    history = await mongo_db.chat_history.find({"user_id": user.id}).to_list(length=100)
    total = len(history)
    mistakes = sum(len(item.get("mistakes", [])) for item in history)
    mistake_rate = round(mistakes / total, 3) if total else 0.0
    report = await mongo_db.weekly_reports.find_one({"user_id": user.id}, sort=[("generated_at", -1)])
    return {
        "user_id": user.id,
        "streak": user.streak,
        "fluency_score": user.fluency_score,
        "cefr_level": user.cefr_level,
        "mistake_rate": mistake_rate,
        "sessions": total,
        "weekly_report": report,
    }
