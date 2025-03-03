from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# Define Priority Enum
class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

# Define Status Enum
class Status(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class Task(BaseModel):
    task_id: Optional[str] = Field(default=None, alias="_id")  # MongoDB ObjectId as string
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Priority = Priority.medium  # Default to "medium"
    status: Status = Status.pending  # Default to "pending"
    user_id: str # Reference to the user who owns the task
    assignee_id: Optional[str] = None  # Reference to the user assigned to the task

    class Config:
        populate_by_name = True  # Allow "_id" to be used as "task_id"
        from_attributes = True  # Convert MongoDB documents to Pydantic models
