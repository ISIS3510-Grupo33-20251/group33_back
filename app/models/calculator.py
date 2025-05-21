from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class GradeEntry(BaseModel):
    name: str
    percentage: float
    value: float

class CalculatorSubject(BaseModel):
    subject_id: str = Field(default=None, alias="_id")
    subject_name: str
    grades: List[GradeEntry] = []
    is_modo_100: bool = False
    created_date: datetime
    last_modified: datetime
    owner_id: str

    class Config:
        from_attributes = True
        populate_by_name = True
