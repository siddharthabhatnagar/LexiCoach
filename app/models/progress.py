from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    words_learned = Column(Integer, default=0)
    grammar_mistakes = Column(Integer, default=0)
    sessions_completed = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    current_interval_days = Column(Integer, default=1)
    ease_factor = Column(Float, default=2.5)
    current_stage = Column(String(50), default="baseline")

    user = relationship("User", backref="progress")
