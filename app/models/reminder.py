from pydantic import BaseModel, Field
from typing import Literal, Optional
from enum import Enum
from datetime import datetime

class ReminderStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DISMISSED = "dismissed"

class ReminderType(str, Enum):
    TASK = "task"
    MEETING = "meeting"
    CUSTOM = "custom"

class Reminder(BaseModel):
    reminder_id: str = Field(default=None, alias="_id")
    user_id: str  # The user who will receive the reminder
    entity_type: Literal["task", "meeting", "custom"]  # The type of entity the reminder is linked to
    entity_id: Optional[str] = Field(default=None)  
    remind_at: datetime  # When the reminder should trigger
    status: ReminderStatus  # Status of the reminder

    class Config:
        from_attributes = True
        populate_by_name = True
        fields = {
            'entity_id': {'exclude': False} 
        }
