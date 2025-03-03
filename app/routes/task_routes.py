#File for API endpoints
from fastapi import APIRouter, HTTPException
from app.database import database
from app.models.task import Task
from bson import ObjectId


router = APIRouter(prefix="/tasks", tags=["Tasks"])

tasks_collection = database["tasks"]  # Reference to the "tasks" collection
users_collection = database["users"]  # Reference to the "users" collection

# Create a new task
@router.post("/", response_model=Task)
async def create_task(task: Task):
    task_dict = task.model_dump(by_alias=True, exclude={"task_id"})
    result = await tasks_collection.insert_one(task_dict)

    # Convert ObjectId to string
    task_dict["_id"] = str(result.inserted_id)
    return task_dict

# Get all tasks
@router.get("/")
async def get_tasks():
    tasks = await tasks_collection.find().to_list(100)
    for task in tasks:
        task["_id"] = str(task["_id"]) # Convert ObjectId to string
    return tasks

# Get a single task by ID
@router.get("/{task_id}")
async def get_task(task_id: str):
    task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    if task:
        task["_id"] = str(task["_id"])
        return task
    raise HTTPException(status_code=404, detail="Task not found")

# Update a task by ID
@router.put("/{task_id}")
async def update_task(task_id: str, updated_task: Task):
    task_dict = updated_task.model_dump(exclude_unset=True, by_alias=True)
    result = await tasks_collection.update_one(
        {"_id": ObjectId(task_id)}, {"$set": task_dict}
    )
    if result.matched_count:
        return {"message": "Task updated successfully"}
    raise HTTPException(status_code=404, detail="Task not found")

# Delete a task by ID
@router.delete("/{task_id}")
async def delete_task(task_id: str):
    result = await tasks_collection.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count:
        return {"message": "Task deleted successfully"}
    raise HTTPException(status_code=404, detail="Task not found")

@router.put("/{task_id}/assign/{user_id}")
async def assign_task_to_user(task_id: str, user_id: str):
    # Check if the user exists
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the task exists
    task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update the task to assign it to the user
    await tasks_collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"assignee_id": user_id}}
    )

    # Add the task to the user's task list if not already there
    if task_id not in user.get("tasks", []):
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"tasks": task_id}}
        )

    return {"message": "Task assigned to user successfully"}
