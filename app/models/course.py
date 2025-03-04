from pydantic import BaseModel, Field
from typing import List, Dict

class Course(BaseModel):
    course_id: str = Field(default=None, alias="_id")
    name: str
    grades: Dict[str, float]  # Assuming the grades are stored as key-value pairs (e.g., {"midterm": 85.0})
    members: List[str] = []  # List of user IDs
    documents: List[str] = []  # List of document IDs
    notes: List[str] = []  # List of note IDs (to be implemented)

    class Config:
        from_attributes = True
        populate_by_name = True
