from fastapi import APIRouter, HTTPException
from app.database import database
from app.models.team import Team
from bson import ObjectId

router = APIRouter(prefix="/teams", tags=["Teams"])

teams_collection = database["teams"]
users_collection = database["users"]  # For checking members

tasks_collection = database["tasks"]  # For checking tasks
documents_collection = database["documents"]  # For checking documents

# Create a new team
@router.post("/", response_model=Team)
async def create_team(team: Team):
    team_dict = team.model_dump(by_alias=True, exclude={"team_id"})
    result = await teams_collection.insert_one(team_dict)
    team_dict["_id"] = str(result.inserted_id)
    return team_dict

# Get all teams
@router.get("/")
async def get_teams():
    teams = await teams_collection.find().to_list(100)
    for team in teams:
        team["_id"] = str(team["_id"])
    return teams

# Get a single team by ID
@router.get("/{team_id}")
async def get_team(team_id: str):
    team = await teams_collection.find_one({"_id": ObjectId(team_id)})
    if team:
        team["_id"] = str(team["_id"])
        return team
    raise HTTPException(status_code=404, detail="Team not found")

# Update a team by ID
@router.put("/{team_id}")
async def update_team(team_id: str, updated_team: Team):
    team_dict = updated_team.model_dump(exclude_unset=True, by_alias=True)
    result = await teams_collection.update_one({"_id": ObjectId(team_id)}, {"$set": team_dict})
    if result.matched_count:
        return {"message": "Team updated successfully"}
    raise HTTPException(status_code=404, detail="Team not found")

# Delete a team by ID
@router.delete("/{team_id}")
async def delete_team(team_id: str):
    result = await teams_collection.delete_one({"_id": ObjectId(team_id)})
    if result.deleted_count:
        return {"message": "Team deleted successfully"}
    raise HTTPException(status_code=404, detail="Team not found")

# Get all members of a team
@router.get("/{team_id}/members")
async def get_team_members(team_id: str):
    team = await teams_collection.find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team.get("members", [])

# Add a member to a team
@router.post("/{team_id}/members/{user_id}")
async def add_member(team_id: str, user_id: str):
    result = await teams_collection.update_one({"_id": ObjectId(team_id)}, {"$addToSet": {"members": user_id}})
    if result.matched_count:
        return {"message": "Member added successfully"}
    raise HTTPException(status_code=404, detail="Team not found")

# Remove a member from a team
@router.delete("/{team_id}/members/{user_id}")
async def remove_member(team_id: str, user_id: str):
    result = await teams_collection.update_one({"_id": ObjectId(team_id)}, {"$pull": {"members": user_id}})
    if result.matched_count:
        return {"message": "Member removed successfully"}
    raise HTTPException(status_code=404, detail="Team not found")

# Get all tasks in the backlog
@router.get("/{team_id}/tasks")
async def get_team_tasks(team_id: str):
    team = await teams_collection.find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team.get("backlog", [])

# Add a task to the backlog
@router.post("/{team_id}/tasks/{task_id}")
async def add_task_to_team(team_id: str, task_id: str):
    result = await teams_collection.update_one({"_id": ObjectId(team_id)}, {"$addToSet": {"backlog": task_id}})
    if result.matched_count:
        return {"message": "Task added to backlog successfully"}
    raise HTTPException(status_code=404, detail="Team not found")

# Remove a task from the backlog
@router.delete("/{team_id}/tasks/{task_id}")
async def remove_task_from_team(team_id: str, task_id: str):
    result = await teams_collection.update_one({"_id": ObjectId(team_id)}, {"$pull": {"backlog": task_id}})
    if result.matched_count:
        return {"message": "Task removed from backlog successfully"}
    raise HTTPException(status_code=404, detail="Team not found")

# Get all documents of a team
@router.get("/{team_id}/documents")
async def get_team_documents(team_id: str):
    team = await teams_collection.find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team.get("documents", [])

# Add a document to the team
@router.post("/{team_id}/documents/{document_id}")
async def add_document_to_team(team_id: str, document_id: str):
    result = await teams_collection.update_one({"_id": ObjectId(team_id)}, {"$addToSet": {"documents": document_id}})
    if result.matched_count:
        return {"message": "Document added to team successfully"}
    raise HTTPException(status_code=404, detail="Team not found")

# Remove a document from the team
@router.delete("/{team_id}/documents/{document_id}")
async def remove_document_from_team(team_id: str, document_id: str):
    result = await teams_collection.update_one({"_id": ObjectId(team_id)}, {"$pull": {"documents": document_id}})
    if result.matched_count:
        return {"message": "Document removed from team successfully"}
    raise HTTPException(status_code=404, detail="Team not found")
