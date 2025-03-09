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
    password: str # Password
    preferences: Optional[Dict] = {}  # JSON-like dictionary
    subscription_status: bool = False  # Default to false
    location: Optional[Location] = None  # Nested location object
    tasks: List[str] = []  # List of task IDs
    documents: List[str] = []  # List of documents IDs
    teams: List[str] = []  # List of team IDs
    friends: List[str] = []  # List of user IDs
    flashcard_decks: List[str] = []  # List of flashcard deck IDs
    courses: List[str] = []  # List of course IDs
    notes: List[str] = []  # List of note IDs

class Config:
        populate_by_name = True
        from_attributes = True  # Allows MongoDB documents to be converted automatically
