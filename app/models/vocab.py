from typing import List
from pydantic import BaseModel

class VocabItem(BaseModel):
    word: str
    definition: str
    example: str
    mnemonic: str
    level: str

class VocabSet(BaseModel):
    user_id: int
    words: List[VocabItem]
    generated_at: str
