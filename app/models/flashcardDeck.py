from pydantic import BaseModel, Field
from typing import List
from enum import Enum

class VisibilityEnum(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"

class FlashcardDeck(BaseModel):
    deck_id: str = Field(default=None, alias="_id")
    name: str
    tags: List[str] = []
    visibility: VisibilityEnum
    owner_id: str  # The user who owns the deck

    class Config:
        from_attributes = True
        populate_by_name = True
