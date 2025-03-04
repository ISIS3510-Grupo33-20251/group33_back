from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

# Define Access Level Enum
class AccessLevel(str, Enum):
    private = "private"
    shared = "shared"
    public = "public"

class Document(BaseModel):
    document_id: Optional[str] = Field(default=None, alias="_id")  # MongoDB ObjectId as string
    name: str
    type: str  # Example: "pdf", "docx", "txt", etc.
    access_level: AccessLevel = AccessLevel.private  # Default to "private"
    user_id: str # Reference to the user who owns the document
    haveAccess: Optional[List[str]] = []  # List of user IDs for the users who have access to the document

class Config:
        populate_by_name = True  # Allow "_id" to be used as "document_id"
        from_attributes = True  # Convert MongoDB documents to Pydantic models
