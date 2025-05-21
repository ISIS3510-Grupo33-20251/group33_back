from pydantic import BaseModel, Field
from typing import List, Optional

class KanbanBoard(BaseModel):
    board_id: Optional[str] = Field(default=None, alias="_id")  # MongoDB ObjectId as string
    name: str
    team_id: str  # The team this board belongs to
    user_id: str  # The user who owns this board
    open_tasks: List[str] = []  # Task IDs in "Open" column
    in_progress_tasks: List[str] = []  # Task IDs in "In Progress"
    in_review_tasks: List[str] = []  # Task IDs in "In Review"
    closed_tasks: List[str] = []  # Task IDs in "Closed"

    class Config:
        populate_by_name = True
        from_attributes = True  # Convert MongoDB documents to Pydantic models
