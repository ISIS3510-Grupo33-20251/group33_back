import uuid

from fastapi import APIRouter, HTTPException, Path
from app.database import database
from app.models.user import User, LoginCredentials, RegisterCredentials, Location
from bson import ObjectId
from app.models.schedule import Schedule  # Asegúrate de que el modelo Schedule esté importado
from app.models.kanbanBoard import KanbanBoard  # Agregar esta importación al inicio del archivo junto con las otras importaciones

router = APIRouter(prefix="/users", tags=["Users"])

users_collection = database["users"]
tasks_collection = database["tasks"]  # Reference to tasks collection for fetching user's tasks
documents_collection = database["documents"]  # Reference to documents collection for fetching user's docs
teams_collection = database["teams"]  # Reference to teams collection for fetching user's teams
flashcard_decks_collection = database["flashcard_decks"]  # Reference to flashcard decks collection for fetching user's flashcard decks
courses_collection = database["courses"]  # Reference to courses collection for fetching user's courses
notes_collection = database["notes"]  # Reference to notes collection for fetching user's notes
schedules_collection = database["schedules"]  # Reference to schedules collection for fetching user's schedules
kanban_collection = database["kanban_boards"]  # Agregar esta línea junto con las otras colecciones

# Generate user flashcards
import flashcards as fc
@router.get("/{user_id}/{subject:path}/flash")
async def get_flashcards(
    user_id: str,
    subject: str = Path(..., title="Subject", description="El subject que puede contener barras")
):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    note_ids = user.get("notes", [])
    object_ids = [ObjectId(note_id) for note_id in note_ids]
    notes = await notes_collection.find({"_id": {"$in": object_ids}}).to_list(100)

    info = ''
    for note in notes:
        if subject in note['subject']:
            info += "\n" + note['content']
    return fc.generar_flashcards(info)

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

# Get all documents for a specific user
@router.get("/{user_id}/documents")
async def get_user_docs(user_id: str):
    # Fetch the user document
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the user's list of docs IDs (if they exist)
    docs_ids = user.get("documents", [])

    # Convert doc ID strings to ObjectId for MongoDB query
    object_ids = [ObjectId(document_id) for document_id in docs_ids]

    # Fetch docs that match those IDs
    docs = await documents_collection.find({"_id": {"$in": object_ids}}).to_list(100)

    # Convert ObjectId to string for API response
    for doc in docs:
        doc["_id"] = str(doc["_id"])

    return docs

# Add a doc to a user
@router.post("/{user_id}/documents/{document_id}")
async def add_document_to_user(user_id: str, document_id: str):
    # Check if the user exists
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the document exists
    document = await documents_collection.find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(status_code=404, detail="document not found")

    # Check if the document is already in the user's document list
    if document_id in user.get("documents", []):
        raise HTTPException(status_code=400, detail="Document already assigned to user")

    # Add document to user's document list
    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"documents": document_id}}
    )

    return {"message": "Document added to user successfully"}

@router.delete("/{user_id}/documents/{document_id}")
async def remove_document_from_user(user_id: str, document_id: str):
    # Check if the user exists
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the document exists
    document = await documents_collection.find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if the document is in the user's document list
    if document_id not in user.get("documents", []):
        raise HTTPException(status_code=400, detail="Document not assigned to user")

    # Remove the document from the user's document list
    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"documents": document_id}}
    )

    return {"message": "Document removed from user successfully"}

# Get all teams for a specific user
@router.get("/{user_id}/teams")
async def get_user_teams(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    team_ids = user.get("teams", [])
    object_ids = [ObjectId(team_id) for team_id in team_ids]
    teams = await teams_collection.find({"_id": {"$in": object_ids}}).to_list(100)

    for team in teams:
        team["_id"] = str(team["_id"])

    return teams

# Add a team to a user
@router.post("/{user_id}/teams/{team_id}")
async def add_team_to_user(user_id: str, team_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    team = await teams_collection.find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if team_id in user.get("teams", []):
        raise HTTPException(status_code=400, detail="Team already assigned to user")

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"teams": team_id}}
    )

    return {"message": "Team added to user successfully"}

# Remove a team from a user
@router.delete("/{user_id}/teams/{team_id}")
async def remove_team_from_user(user_id: str, team_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    team = await teams_collection.find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if team_id not in user.get("teams", []):
        raise HTTPException(status_code=400, detail="Team not assigned to user")

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"teams": team_id}}
    )

    return {"message": "Team removed from user successfully"}

# Get all friends for a specific user
@router.get("/{user_id}/friends")
async def get_user_friends(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    friend_ids = user.get("friends", [])
    object_ids = [ObjectId(friend_id) for friend_id in friend_ids]
    friends = await users_collection.find({"_id": {"$in": object_ids}}).to_list(100)

    for friend in friends:
        friend["_id"] = str(friend["_id"])

    return friends

# Add a friend to a user
@router.post("/{user_id}/friends/{friend_id}")
async def add_friend_to_user(user_id: str, friend_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    friend = await users_collection.find_one({"_id": ObjectId(friend_id)})
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")

    if friend_id in user.get("friends", []):
        raise HTTPException(status_code=400, detail="Friend already added to user")

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"friends": friend_id}}
    )

    return {"message": "Friend added to user successfully"}

# Remove a friend from a user
@router.delete("/{user_id}/friends/{friend_id}")
async def remove_friend_from_user(user_id: str, friend_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    friend = await users_collection.find_one({"_id": ObjectId(friend_id)})
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")

    if friend_id not in user.get("friends", []):
        raise HTTPException(status_code=400, detail="Friend not added to user")

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"friends": friend_id}}
    )

    return {"message": "Friend removed from user successfully"}

# Get all flashcard decks for a specific user
@router.get("/{user_id}/flashcard_decks")
async def get_user_flashcard_decks(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    deck_ids = user.get("flashcard_decks", [])
    object_ids = [ObjectId(deck_id) for deck_id in deck_ids]
    flashcard_decks = await flashcard_decks_collection.find({"_id": {"$in": object_ids}}).to_list(100)

    for deck in flashcard_decks:
        deck["_id"] = str(deck["_id"])

    return

# Add a flashcard deck to a user
@router.post("/{user_id}/flashcard_decks/{deck_id}")
async def add_flashcard_deck_to_user(user_id: str, deck_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    deck = await flashcard_decks_collection.find_one({"_id": ObjectId(deck_id)})
    if not deck:
        raise HTTPException(status_code=404, detail="Flashcard deck not found")

    if deck_id in user.get("flashcard_decks", []):
        raise HTTPException(status_code=400, detail="Flashcard deck already assigned to user")

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"flashcard_decks": deck_id}}
    )

    return {"message": "Flashcard deck added to user successfully"}

# Remove a flashcard deck from a user
@router.delete("/{user_id}/flashcard_decks/{deck_id}")
async def remove_flashcard_deck_from_user(user_id: str, deck_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    deck = await flashcard_decks_collection.find_one({"_id": ObjectId(deck_id)})
    if not deck:
        raise HTTPException(status_code=404, detail="Flashcard deck not found")

    if deck_id not in user.get("flashcard_decks", []):
        raise HTTPException(status_code=400, detail="Flashcard deck not assigned to user")

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"flashcard_decks": deck_id}}
    )

    return {"message": "Flashcard deck removed from user successfully"}

# Get all courses for a specific user
@router.get("/{user_id}/courses")
async def get_user_courses(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    course_ids = user.get("courses", [])
    object_ids = [ObjectId(course_id) for course_id in course_ids]
    courses = await courses_collection.find({"_id": {"$in": object_ids}}).to_list(100)

    for course in courses:
        course["_id"] = str(course["_id"])

    return courses

# Add a course to a user
@router.post("/{user_id}/courses/{course_id}")
async def add_course_to_user(user_id: str, course_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    course = await courses_collection.find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course_id in user.get("courses", []):
        raise HTTPException(status_code=400, detail="Course already assigned to user")

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"courses": course_id}}
    )

    return {"message": "Course added to user successfully"}

# Remove a course from a user
@router.delete("/{user_id}/courses/{course_id}")
async def remove_course_from_user(user_id: str, course_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    course = await courses_collection.find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course_id not in user.get("courses", []):
        raise HTTPException(status_code=400, detail="Course not assigned to user")

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"courses": course_id}}
    )

    return {"message": "Course removed from user successfully"}

# Get all notes for a specific user
@router.get("/{user_id}/notes")
async def get_user_notes(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    note_ids = user.get("notes", [])
    object_ids = [ObjectId(note_id) for note_id in note_ids]
    notes = await notes_collection.find({"_id": {"$in": object_ids}}).to_list(100)

    for note in notes:
        note["_id"] = str(note["_id"])

    return notes

# Add a note to a user
@router.post("/{user_id}/notes/{note_id}")
async def add_note_to_user(user_id: str, note_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    note = await notes_collection.find_one({"_id": ObjectId(note_id)})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if note_id in user.get("notes", []):
        raise HTTPException(status_code=400, detail="Note already assigned to user")

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"notes": note_id}}
    )

    return {"message": "Note added to user successfully"}

# Remove a note from a user
@router.delete("/{user_id}/notes/{note_id}")
async def remove_note_from_user(user_id: str, note_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    note = await notes_collection.find_one({"_id": ObjectId(note_id)})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if note_id not in user.get("notes", []):
        raise HTTPException(status_code=400, detail="Note not assigned to user")

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"notes": note_id}}
    )

    return {"message": "Note removed from user successfully"}

# Authentication routes
@router.post("/auth/login")
async def login(credentials: LoginCredentials):
    user = await users_collection.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # In production, use proper password hashing
    if user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate a simple token (in production, use JWT)
    token = str(uuid.uuid4())

    return {
        "token": token,
        "userId": str(user["_id"]),
        "email": user["email"],
        "name": user["name"]
    }

@router.post("/auth/register")
async def register(user_data: RegisterCredentials):
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_dict = {
        "name": user_data.name,
        "email": user_data.email,
        "password": user_data.password,
        "preferences": {},
        "subscription_status": False,
        "tasks": [],
        "documents": [],
        "teams": [],
        "friends": [],
        "flashcard_decks": [],
        "courses": [],
        "notes": []
    }

    result = await users_collection.insert_one(user_dict)

    # Generate token
    token = str(uuid.uuid4())

    return {
        "token": token,
        "userId": str(result.inserted_id),
        "email": user_data.email,
        "name": user_data.name
    }

# Update user location
@router.put("/{user_id}/location")
async def update_user_location(
        user_id: str,
        location: Location):

    # Update just the location
    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"location": location.dict()}}
    )

    if result.matched_count:
        return {"message": "Location updated successfully"}
    raise HTTPException(status_code=404, detail="User not found")

# Get friends with location data
@router.get("/{user_id}/friends/location")
async def get_friends_with_location(
        user_id: str):

    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get user's friends
    friend_ids = user.get("friends", [])
    if not friend_ids:
        return []

    # Convert friend IDs to ObjectId
    friend_object_ids = [ObjectId(friend_id) for friend_id in friend_ids]

    # Find friends with location data
    friends_with_location = await users_collection.find({
        "_id": {"$in": friend_object_ids},
        "location": {"$exists": True, "$ne": None}
    }).to_list(100)

    # Format the response
    result = []
    for friend in friends_with_location:
        friend_dto = {
            "_id": str(friend["_id"]),
            "name": friend["name"],
            "email": friend["email"],
            "password": friend["password"],
            "location": friend.get("location")
        }

        # Add optional fields if they exist
        if "preferences" in friend:
            friend_dto["preferences"] = friend["preferences"]
        if "subscription_status" in friend:
            friend_dto["subscription_status"] = friend["subscription_status"]

        result.append(friend_dto)

    return result

# Get or create a schedule for a specific user
@router.get("/{user_id}/schedule")
async def get_or_create_user_schedule(user_id: str):
    # Check if the user exists
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the user already has a schedule
    schedule = await schedules_collection.find_one({"user_id": user_id})
    
    if schedule:
        return {"schedule_id": str(schedule["_id"])}  # Return existing schedule ID

    # Create a new schedule if none exists
    new_schedule = Schedule(user_id=user_id)  # Asegúrate de que el modelo Schedule tenga un campo user_id
    schedule_dict = new_schedule.model_dump(by_alias=True, exclude={"schedule_id"})
    result = await schedules_collection.insert_one(schedule_dict)
    schedule_dict["_id"] = str(result.inserted_id)

    return {"schedule_id": schedule_dict["_id"]}  # Return new schedule ID

# Get or create a kanban for a specific user
@router.get("/{user_id}/kanban")
async def get_or_create_user_kanban(user_id: str):
    try:
        # Check if the user exists
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if the user already has a kanban
        kanban = await kanban_collection.find_one({"user_id": user_id})
        
        if kanban:
            return {"kanban_id": str(kanban["_id"])}  # Return existing kanban ID

        # Create a new kanban if none exists
        new_kanban = KanbanBoard(
            name="Personal Board",
            team_id=user_id,  # Using user_id as team_id for personal boards
            user_id=user_id
        )
        kanban_dict = new_kanban.model_dump(by_alias=True, exclude={"board_id"})
        result = await kanban_collection.insert_one(kanban_dict)
        kanban_dict["_id"] = str(result.inserted_id)

        return {"kanban_id": kanban_dict["_id"]}  # Return new kanban ID
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
