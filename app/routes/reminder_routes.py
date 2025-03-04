from fastapi import APIRouter, HTTPException
from app.database import database
from app.models.reminder import Reminder
from bson import ObjectId

router = APIRouter(prefix="/reminders", tags=["Reminders"])

reminders_collection = database["reminders"]

# Create a new reminder
@router.post("/", response_model=Reminder)
async def create_reminder(reminder: Reminder):
    reminder_dict = reminder.model_dump(by_alias=True, exclude={"reminder_id"})
    result = await reminders_collection.insert_one(reminder_dict)
    reminder_dict["_id"] = str(result.inserted_id)
    return reminder_dict

# Get all reminders
@router.get("/")
async def get_reminders():
    reminders = await reminders_collection.find().to_list(100)
    for reminder in reminders:
        reminder["_id"] = str(reminder["_id"])
    return reminders

# Get a single reminder by ID
@router.get("/{reminder_id}")
async def get_reminder(reminder_id: str):
    reminder = await reminders_collection.find_one({"_id": ObjectId(reminder_id)})
    if reminder:
        reminder["_id"] = str(reminder["_id"])
        return reminder
    raise HTTPException(status_code=404, detail="Reminder not found")

# Update a reminder by ID
@router.put("/{reminder_id}")
async def update_reminder(reminder_id: str, updated_reminder: Reminder):
    reminder_dict = updated_reminder.model_dump(exclude_unset=True, by_alias=True)
    result = await reminders_collection.update_one({"_id": ObjectId(reminder_id)}, {"$set": reminder_dict})
    if result.matched_count:
        return {"message": "Reminder updated successfully"}
    raise HTTPException(status_code=404, detail="Reminder not found")

# Delete a reminder by ID
@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: str):
    result = await reminders_collection.delete_one({"_id": ObjectId(reminder_id)})
    if result.deleted_count:
        return {"message": "Reminder deleted successfully"}
    raise HTTPException(status_code=404, detail="Reminder not found")

# Get all reminders for a specific user
@router.get("/user/{user_id}")
async def get_reminders_for_user(user_id: str):
    reminders = await reminders_collection.find({"user_id": user_id}).to_list(100)
    for reminder in reminders:
        reminder["_id"] = str(reminder["_id"])
    return reminders

# Get all reminders for a specific task
@router.get("/task/{task_id}")
async def get_reminders_for_task(task_id: str):
    reminders = await reminders_collection.find({"entity_id": task_id, "entity_type": "task"}).to_list(100)
    for reminder in reminders:
        reminder["_id"] = str(reminder["_id"])
    return reminders

# Get all reminders for a specific meeting
@router.get("/meeting/{meeting_id}")
async def get_reminders_for_meeting(meeting_id: str):
    reminders = await reminders_collection.find({"entity_id": meeting_id, "entity_type": "meeting"}).to_list(100)
    for reminder in reminders:
        reminder["_id"] = str(reminder["_id"])
    return reminders
