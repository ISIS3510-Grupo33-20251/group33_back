from fastapi import APIRouter, HTTPException
from app.database import database
from app.models.meeting import Meeting
from bson import ObjectId

router = APIRouter(prefix="/meetings", tags=["Meetings"])

meetings_collection = database["meetings"]
users_collection = database["users"]  # For checking participants

# Create a new meeting
@router.post("/", response_model=Meeting)
async def create_meeting(meeting: Meeting):
    meeting_dict = meeting.model_dump(by_alias=True, exclude={"meeting_id"})
    result = await meetings_collection.insert_one(meeting_dict)
    meeting_dict["_id"] = str(result.inserted_id)
    return meeting_dict

# Get all meetings
@router.get("/")
async def get_meetings():
    meetings = await meetings_collection.find().to_list(100)
    for meeting in meetings:
        meeting["_id"] = str(meeting["_id"])
    return meetings

# Get a single meeting by ID
@router.get("/{meeting_id}")
async def get_meeting(meeting_id: str):
    meeting = await meetings_collection.find_one({"_id": ObjectId(meeting_id)})
    if meeting:
        meeting["_id"] = str(meeting["_id"])
        return meeting
    raise HTTPException(status_code=404, detail="Meeting not found")

# Update a meeting by ID
@router.put("/{meeting_id}")
async def update_meeting(meeting_id: str, updated_meeting: Meeting):
    meeting_dict = updated_meeting.model_dump(exclude_unset=True, by_alias=True)
    result = await meetings_collection.update_one({"_id": ObjectId(meeting_id)}, {"$set": meeting_dict})
    if result.matched_count:
        return {"message": "Meeting updated successfully"}
    raise HTTPException(status_code=404, detail="Meeting not found")

# Delete a meeting by ID
@router.delete("/{meeting_id}")
async def delete_meeting(meeting_id: str):
    result = await meetings_collection.delete_one({"_id": ObjectId(meeting_id)})
    if result.deleted_count:
        return {"message": "Meeting deleted successfully"}
    raise HTTPException(status_code=404, detail="Meeting not found")

# Get all participants of a meeting
@router.get("/{meeting_id}/participants")
async def get_meeting_participants(meeting_id: str):
    meeting = await meetings_collection.find_one({"_id": ObjectId(meeting_id)})
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting.get("participants", [])

# Add a participant to a meeting
@router.post("/{meeting_id}/participants/{user_id}")
async def add_participant(meeting_id: str, user_id: str):
    result = await meetings_collection.update_one({"_id": ObjectId(meeting_id)}, {"$addToSet": {"participants": user_id}})
    if result.matched_count:
        return {"message": "Participant added successfully"}
    raise HTTPException(status_code=404, detail="Meeting not found")

# Remove a participant from a meeting
@router.delete("/{meeting_id}/participants/{user_id}")
async def remove_participant(meeting_id: str, user_id: str):
    result = await meetings_collection.update_one({"_id": ObjectId(meeting_id)}, {"$pull": {"participants": user_id}})
    if result.matched_count:
        return {"message": "Participant removed successfully"}
    raise HTTPException(status_code=404, detail="Meeting not found")
