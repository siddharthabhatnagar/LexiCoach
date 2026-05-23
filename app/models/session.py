from typing import Optional
from pydantic import BaseModel

class SessionContext(BaseModel):
    user_id: int
    roleplay: Optional[str] = None
    last_message: Optional[str] = None
    conversation_id: Optional[str] = None
