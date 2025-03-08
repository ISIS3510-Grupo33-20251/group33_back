from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class Note(BaseModel):
    note_id: str = Field(default=None, alias="_id")
    title: str
    subject: str
    content: str
    tags: List[str] = []
    created_date: datetime
    last_modified: datetime
    owner_id: str  # The user who owns the note

    class Config:
        from_attributes = True
        populate_by_name = True
