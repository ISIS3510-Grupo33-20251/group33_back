from fastapi import APIRouter, HTTPException
from app.database import database
from app.models.user import User
from bson import ObjectId

router = APIRouter(prefix="/users", tags=["Users"])

users_collection = database["users"]
tasks_collection = database["tasks"]  # Reference to tasks collection for fetching user's tasks

# Create a new user
@router.post("/", response_model=User)
async def create_user(user: User):
    user_dict = user.model_dump(by_alias=True, exclude={"user_id"})
    result = await users_collection.insert_one(user_dict)

    # Set the created _id
    user_dict["_id"] = str(result.inserted_id)
    return user_dict

# Get all users
@router.get("/")
async def get_users():
    users = await users_collection.find().to_list(100)
    for user in users:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
    return users

# Get a single user by ID
@router.get("/{user_id}")
async def get_user(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user["_id"] = str(user["_id"])
        return user
    raise HTTPException(status_code=404, detail="User not found")

# Update a user by ID
@router.put("/{user_id}")
async def update_user(user_id: str, updated_user: User):
    user_dict = updated_user.model_dump(exclude_unset=True, by_alias=True)
    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": user_dict}
    )
    if result.matched_count:
        return {"message": "User updated successfully"}
    raise HTTPException(status_code=404, detail="User not found")

# Delete a user by ID
@router.delete("/{user_id}")
async def delete_user(user_id: str):
    result = await users_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count:
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")

# Get all tasks for a specific user
@router.get("/{user_id}/tasks")
async def get_user_tasks(user_id: str):
    # Fetch the user document
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the user's list of task IDs (if they exist)
    task_ids = user.get("tasks", [])

    # Convert task ID strings to ObjectId for MongoDB query
    object_ids = [ObjectId(task_id) for task_id in task_ids]

    # Fetch tasks that match those IDs
    tasks = await tasks_collection.find({"_id": {"$in": object_ids}}).to_list(100)

    # Convert ObjectId to string for API response
    for task in tasks:
        task["_id"] = str(task["_id"])

    return tasks

# Add a task to a user
@router.post("/{user_id}/tasks/{task_id}")
async def add_task_to_user(user_id: str, task_id: str):
    # Check if the user exists
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the task exists
    task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if the task is already in the user's task list
    if task_id in user.get("tasks", []):
        raise HTTPException(status_code=400, detail="Task already assigned to user")

    # Add task to user's task list
    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"tasks": task_id}}
    )

    return {"message": "Task added to user successfully"}

@router.delete("/{user_id}/tasks/{task_id}")
async def remove_task_from_user(user_id: str, task_id: str):
    # Check if the user exists
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the task exists
    task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if the task is in the user's task list
    if task_id not in user.get("tasks", []):
        raise HTTPException(status_code=400, detail="Task not assigned to user")

    # Remove the task from the user's task list
    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"tasks": task_id}}
    )

    return {"message": "Task removed from user successfully"}

