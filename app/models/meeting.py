from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Meeting(BaseModel):
    meeting_id: str = Field(default=None, alias="_id")
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    host_id: str  # The user who created the meeting
    participants: List[str] = []  # List of user IDs attending
    color: Optional[str] = "#4285F4"  # Default color in hex format (Google Blue)
    day_of_week: int 

    class Config:
        from_attributes = True
        populate_by_name = True
