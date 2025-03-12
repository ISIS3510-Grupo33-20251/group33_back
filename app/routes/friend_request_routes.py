from fastapi import APIRouter, HTTPException
from app.database import database
from app.models.friendRequest import FriendRequest, FriendRequestStatus
from bson import ObjectId
import time

router = APIRouter(prefix="/friend_requests", tags=["Friend Requests"])

friend_requests_collection = database["friend_requests"]
users_collection = database["users"]

# Create a new friend request
@router.post("/", response_model=FriendRequest)
async def create_friend_request(sender_id: str, receiver_id: str):
    existing = await friend_requests_collection.find_one({
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "status": FriendRequestStatus.PENDING
    })

    if existing:
        raise HTTPException(status_code=400, detail="Friend request already sent")

    # Create new request
    request = {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "status": FriendRequestStatus.PENDING,
        "created_at": time.time()
    }

    result = await friend_requests_collection.insert_one(request)
    request["_id"] = str(result.inserted_id)

    return request

# Create a new friend request by email
@router.post("/by_email", response_model=FriendRequest)
async def create_friend_request_by_email(request: dict):
    sender_id = request.get("senderId")
    email = request.get("email")

    if not sender_id:
        raise HTTPException(status_code=400, detail="Sender ID is required")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    # Find user by email
    receiver = await users_collection.find_one({"email": email})
    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")

    receiver_id = str(receiver["_id"])

    existing = await friend_requests_collection.find_one({
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "status": FriendRequestStatus.PENDING
    })

    if existing:
        raise HTTPException(status_code=400, detail="Friend request already sent")

    # Create new request
    request_data = {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "status": FriendRequestStatus.PENDING,
        "created_at": time.time()
    }

    result = await friend_requests_collection.insert_one(request_data)
    request_data["_id"] = str(result.inserted_id)

    return request_data

# Get pending requests for a user
@router.get("/pending/{user_id}")
async def get_pending_requests(user_id: str):
    requests = await friend_requests_collection.find({
        "receiver_id": user_id,
        "status": FriendRequestStatus.PENDING
    }).to_list(100)

    for request in requests:
        request["_id"] = str(request["_id"])

    return requests

# Accept a friend request
@router.post("/{request_id}/accept")
async def accept_friend_request(request_id: str):
    request = await friend_requests_collection.find_one({"_id": ObjectId(request_id)})

    if not request:
        raise HTTPException(status_code=404, detail="Friend request not found")

    if request["status"] != FriendRequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already processed")

    # Update request status
    await friend_requests_collection.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {"status": FriendRequestStatus.ACCEPTED}}
    )

    # Add each user to the other's friends list
    await users_collection.update_one(
        {"_id": ObjectId(request["sender_id"])},
        {"$addToSet": {"friends": request["receiver_id"]}}
    )

    await users_collection.update_one(
        {"_id": ObjectId(request["receiver_id"])},
        {"$addToSet": {"friends": request["sender_id"]}}
    )

    return {"message": "Friend request accepted"}
