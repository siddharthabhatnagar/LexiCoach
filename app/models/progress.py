from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class Progress(BaseModel):
    """Pydantic model representing user progress - stored in Firestore."""
    email: str
    words_learned: int = 0
    grammar_mistakes: int = 0
    sessions_completed: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    current_interval_days: int = 1
    ease_factor: float = 2.5
    current_stage: str = "baseline"
