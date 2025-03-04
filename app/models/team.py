from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId

class Team(BaseModel):
    team_id: Optional[str] = Field(default=None, alias="_id")  # MongoDB ObjectId as string
    name: str
    description: str
    subject: str
    owner_id: str  # User who owns the team
    members: List[str] = []  # List of user IDs who are team members
    backlog: List[str] = []  # List of task IDs in the backlog
    documents: List[str] = []  # List of document IDs related to the team
    kanban: str # Reference to the kanban board

    class Config:
        populate_by_name = True  # Allow "_id" to be used as "team_id"
        from_attributes = True  # Convert MongoDB documents to Pydantic models
