from fastapi import APIRouter, Depends
import logging
from app.core.dependencies import get_current_user
from app.services.user_service import User
from app.db.firebase import get_firestore_db

router = APIRouter()

@router.get("/stats")
async def progress_stats(user: User = Depends(get_current_user)):
    try:
        db = get_firestore_db()
        
        # Get chat history for stats
        history_docs = db.collection("chat_history").where("email", "==", user.email).limit(100).stream()
        history = [doc.to_dict() for doc in history_docs]
        
        total = len(history)
        mistakes = sum(len(item.get("mistakes", [])) for item in history)
        mistake_rate = round(mistakes / total, 3) if total else 0.0
        
        # Get latest weekly report
        report_docs = db.collection("weekly_reports").where("email", "==", user.email).order_by("generated_at", direction="DESCENDING").limit(1).stream()
        report = next(report_docs, None)
        if report:
            report = report.to_dict()
    except Exception as e:
        logging.error(f"Error fetching progress stats: {e}")
        total = 0
        mistake_rate = 0.0
        report = None

    return {
        "email": user.email,
        "full_name": getattr(user, "full_name", None),
        "mistake_rate": mistake_rate,
        "sessions": total,
        "weekly_report": report,
    }
