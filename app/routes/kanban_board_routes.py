from fastapi import APIRouter, HTTPException
from app.database import database
from app.models.kanbanBoard import KanbanBoard
from bson import ObjectId

router = APIRouter(prefix="/kanban", tags=["Kanban Board"])

kanban_collection = database["kanban_boards"]
tasks_collection = database["tasks"]  # For checking task existence

# Create a new Kanban board
@router.post("/", response_model=KanbanBoard)
async def create_kanban_board(board: KanbanBoard):
    board_dict = board.model_dump(by_alias=True, exclude={"board_id"})
    result = await kanban_collection.insert_one(board_dict)
    board_dict["_id"] = str(result.inserted_id)
    return board_dict

# Get all Kanban boards
@router.get("/")
async def get_kanban_boards():
    boards = await kanban_collection.find().to_list(100)
    for board in boards:
        board["_id"] = str(board["_id"])
    return boards

# Get a single Kanban board by ID
@router.get("/{board_id}")
async def get_kanban_board(board_id: str):
    board = await kanban_collection.find_one({"_id": ObjectId(board_id)})
    if board:
        board["_id"] = str(board["_id"])
        return board
    raise HTTPException(status_code=404, detail="Kanban board not found")

# Add a task to the board
@router.post("/{board_id}/tasks/{task_id}")
async def add_task_to_board(board_id: str, task_id: str):
    # Check if the task exists
    task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if the board exists
    board = await kanban_collection.find_one({"_id": ObjectId(board_id)})
    if not board:
        raise HTTPException(status_code=404, detail="Kanban board not found")

    # Check if the task is already in the board
    if task_id in board.get("all_tasks", []):
        raise HTTPException(status_code=400, detail="Task already in board")

    # Add task to all_tasks and open_tasks
    result = await kanban_collection.update_one(
        {"_id": ObjectId(board_id)},
        {
            "$push": {
                "all_tasks": task_id,
                "open_tasks": task_id
            }
        }
    )

    if result.modified_count:
        return {"message": "Task added to board successfully"}
    raise HTTPException(status_code=500, detail="Failed to add task to board")

# Delete a Kanban board by ID
@router.delete("/{board_id}")
async def delete_kanban_board(board_id: str):
    result = await kanban_collection.delete_one({"_id": ObjectId(board_id)})
    if result.deleted_count:
        return {"message": "Kanban board deleted successfully"}
    raise HTTPException(status_code=404, detail="Kanban board not found")

# Move a task from Open to In Progress
@router.post("/{board_id}/move/open-to-inprogress/{task_id}")
async def move_task_open_to_in_progress(board_id: str, task_id: str):
    result = await kanban_collection.update_one(
        {"_id": ObjectId(board_id)},
        {"$pull": {"open_tasks": task_id}, "$push": {"in_progress_tasks": task_id}}
    )
    if result.matched_count:
        return {"message": "Task moved to In Progress"}
    raise HTTPException(status_code=404, detail="Board or Task not found")

# Move a task from In Progress to In Review
@router.post("/{board_id}/move/inprogress-to-inreview/{task_id}")
async def move_task_in_progress_to_in_review(board_id: str, task_id: str):
    result = await kanban_collection.update_one(
        {"_id": ObjectId(board_id)},
        {"$pull": {"in_progress_tasks": task_id}, "$push": {"in_review_tasks": task_id}}
    )
    if result.matched_count:
        return {"message": "Task moved to In Review"}
    raise HTTPException(status_code=404, detail="Board or Task not found")

# Move a task from In Review to Closed
@router.post("/{board_id}/move/inreview-to-closed/{task_id}")
async def move_task_in_review_to_closed(board_id: str, task_id: str):
    result = await kanban_collection.update_one(
        {"_id": ObjectId(board_id)},
        {"$pull": {"in_review_tasks": task_id}, "$push": {"closed_tasks": task_id}}
    )
    if result.matched_count:
        return {"message": "Task moved to Closed"}
    raise HTTPException(status_code=404, detail="Board or Task not found")

# Move a task from In Progress to Closed
@router.post("/{board_id}/move/inprogress-to-closed/{task_id}")
async def move_task_in_progress_to_closed(board_id: str, task_id: str):
    result = await kanban_collection.update_one(
        {"_id": ObjectId(board_id)},
        {"$pull": {"in_progress_tasks": task_id}, "$push": {"closed_tasks": task_id}}
    )
    if result.matched_count:
        return {"message": "Task moved directly to Closed"}
    raise HTTPException(status_code=404, detail="Board or Task not found")

# Remove a task from the board
@router.delete("/{board_id}/tasks/{task_id}")
async def remove_task_from_board(board_id: str, task_id: str):
    # Remove task from all lists
    result = await kanban_collection.update_one(
        {"_id": ObjectId(board_id)},
        {
            "$pull": {
                "all_tasks": task_id,
                "open_tasks": task_id,
                "in_progress_tasks": task_id,
                "in_review_tasks": task_id,
                "closed_tasks": task_id
            }
        }
    )
    if result.modified_count:
        return {"message": "Task removed from board successfully"}
    raise HTTPException(status_code=404, detail="Board or Task not found")
