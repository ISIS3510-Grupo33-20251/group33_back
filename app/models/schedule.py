from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class Schedule(BaseModel):
    schedule_id: Optional[str] = Field(default=None, alias="_id")  # MongoDB ObjectId as string
    user_id: str  # Reference to the user who owns the schedule
    meetings: List[str] = []  # List of meeting IDs

    class Config:
        populate_by_name = True  # Allow "_id" to be used as "schedule_id"
        from_attributes = True  # Convert MongoDB documents to Pydantic models
