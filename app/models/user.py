from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict
from bson import ObjectId
from typing import List

# Location Schema
class Location(BaseModel):
    latitude: float
    longitude: float

# User Schema
class User(BaseModel):
    user_id: Optional[str] = Field(default=None, alias="_id")  # MongoDB ObjectId as string
    name: str
    email: EmailStr  # Enforces valid email format
    preferences: Optional[Dict] = {}  # JSON-like dictionary
    subscription_status: bool = False  # Default to false
    location: Optional[Location] = None  # Nested location object
    tasks: Optional[List[str]] = []  # List of task IDs

    class Config:
        populate_by_name = True
        from_attributes = True  # Allows MongoDB documents to be converted automatically
