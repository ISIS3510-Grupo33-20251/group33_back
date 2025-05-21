from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class GradeEntry(BaseModel):
    name: str
    percentage: float
    grade: float

class CalculatorSubject(BaseModel):
    calculator_id: Optional[str] = Field(default=None, alias="_id")
    subject_name: str
    owner_id: str
    entries: List[GradeEntry] = []
    created_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True
