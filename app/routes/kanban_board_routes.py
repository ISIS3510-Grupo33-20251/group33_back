from fastapi import APIRouter, HTTPException
from app.database import database
from app.models.kanban_board import KanbanBoard
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
