from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class FriendRequestStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class FriendRequest(BaseModel):
    request_id: Optional[str] = Field(default=None, alias="_id")
    sender_id: str
    receiver_id: str
    status: FriendRequestStatus = FriendRequestStatus.PENDING
    created_at: float  # Unix timestamp

    class Config:
        from_attributes = True
        populate_by_name = True