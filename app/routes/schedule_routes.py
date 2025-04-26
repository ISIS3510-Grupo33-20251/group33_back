from fastapi import APIRouter, HTTPException
from app.database import database
from app.models.schedule import Schedule
from bson import ObjectId

router = APIRouter(prefix="/schedules", tags=["Schedules"])

schedules_collection = database["schedules"]
users_collection = database["users"]  # For user validation
meetings_collection = database["meetings"]  # For meeting validation

# Create a new schedule
@router.post("/", response_model=Schedule)
async def create_schedule(schedule: Schedule):
    # Ensure the user exists
    user = await users_collection.find_one({"_id": ObjectId(schedule.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Ensure the user_id is set in the schedule
    if not schedule.user_id:
        raise HTTPException(status_code=400, detail="User ID must be provided")
    schedule.user_id = str(user["_id"])  # Asegúrate de que el user_id esté presente

    schedule_dict = schedule.model_dump(by_alias=True, exclude={"schedule_id"})
    result = await schedules_collection.insert_one(schedule_dict)
    schedule_dict["_id"] = str(result.inserted_id)
    return schedule_dict

# Get all schedules
@router.get("/")
async def get_schedules():
    schedules = await schedules_collection.find().to_list(100)
    for schedule in schedules:
        schedule["_id"] = str(schedule["_id"])
    return schedules

# Get a schedule by ID
@router.get("/{schedule_id}")
async def get_schedule(schedule_id: str):
    schedule = await schedules_collection.find_one({"_id": ObjectId(schedule_id)})
    if schedule:
        schedule["_id"] = str(schedule["_id"])
        return schedule
    raise HTTPException(status_code=404, detail="Schedule not found")

# Update a schedule
@router.put("/{schedule_id}")
async def update_schedule(schedule_id: str, updated_schedule: Schedule):
    schedule_dict = updated_schedule.model_dump(exclude_unset=True, by_alias=True)
    result = await schedules_collection.update_one({"_id": ObjectId(schedule_id)}, {"$set": schedule_dict})
    if result.matched_count:
        return {"message": "Schedule updated successfully"}
    raise HTTPException(status_code=404, detail="Schedule not found")

# Delete a schedule
@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: str):
    result = await schedules_collection.delete_one({"_id": ObjectId(schedule_id)})
    if result.deleted_count:
        return {"message": "Schedule deleted successfully"}
    raise HTTPException(status_code=404, detail="Schedule not found")

# Get all meetings in a schedule
@router.get("/{schedule_id}/meetings")
async def get_schedule_meetings(schedule_id: str):
    schedule = await schedules_collection.find_one({"_id": ObjectId(schedule_id)})
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule.get("meetings", [])

# Add a meeting to a schedule
@router.post("/{schedule_id}/meetings/{meeting_id}")
async def add_meeting_to_schedule(schedule_id: str, meeting_id: str):
    # Ensure schedule exists
    schedule = await schedules_collection.find_one({"_id": ObjectId(schedule_id)})
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Ensure meeting exists
    meeting = await meetings_collection.find_one({"_id": ObjectId(meeting_id)})
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Add meeting to the schedule
    result = await schedules_collection.update_one(
        {"_id": ObjectId(schedule_id)},
        {"$addToSet": {"meetings": meeting_id}}
    )
    if result.matched_count:
        return {"message": "Meeting added to schedule successfully"}
    raise HTTPException(status_code=404, detail="Schedule not found")

# Remove a meeting from a schedule
@router.delete("/{schedule_id}/meetings/{meeting_id}")
async def remove_meeting_from_schedule(schedule_id: str, meeting_id: str):
    # Ensure schedule exists
    schedule = await schedules_collection.find_one({"_id": ObjectId(schedule_id)})
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Remove the meeting from the schedule
    result = await schedules_collection.update_one(
        {"_id": ObjectId(schedule_id)},
        {"$pull": {"meetings": meeting_id}}
    )
    if result.matched_count:
        return {"message": "Meeting removed from schedule successfully"}
    raise HTTPException(status_code=404, detail="Schedule not found")
