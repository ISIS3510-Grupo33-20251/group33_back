from fastapi import APIRouter, HTTPException
from app.database import database
from app.models.note import Note
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/notes", tags=["Notes"])

notes_collection = database["notes"]

# Create a new note
@router.post("/", response_model=Note)
async def create_note(note: Note):
    note_dict = note.model_dump(by_alias=True, exclude={"note_id"})
    note_dict["created_date"] = datetime.utcnow()
    note_dict["last_modified"] = datetime.utcnow()
    result = await notes_collection.insert_one(note_dict)
    note_dict["_id"] = str(result.inserted_id)
    return note_dict

# Get all notes
@router.get("/")
async def get_notes():
    notes = await notes_collection.find().to_list(100)
    for note in notes:
        note["_id"] = str(note["_id"])
    return notes

# Get a single note by ID
@router.get("/{note_id}")
async def get_note(note_id: str):
    note = await notes_collection.find_one({"_id": ObjectId(note_id)})
    if note:
        note["_id"] = str(note["_id"])
        return note
    raise HTTPException(status_code=404, detail="Note not found")

# Update a note by ID
@router.put("/{note_id}")
async def update_note(note_id: str, updated_note: Note):
    note_dict = updated_note.model_dump(exclude_unset=True, by_alias=True)
    note_dict["last_modified"] = datetime.utcnow()
    result = await notes_collection.update_one({"_id": ObjectId(note_id)}, {"$set": note_dict})
    if result.matched_count:
        return {"message": "Note updated successfully"}
    raise HTTPException(status_code=404, detail="Note not found")

# Delete a note by ID
@router.delete("/{note_id}")
async def delete_note(note_id: str):
    result = await notes_collection.delete_one({"_id": ObjectId(note_id)})
    if result.deleted_count:
        return {"message": "Note deleted successfully"}
    raise HTTPException(status_code=404, detail="Note not found")

# Get all notes by subject
@router.get("/subject/{subject}")
async def get_notes_by_subject(subject: str):
    notes = await notes_collection.find({"subject": subject}).to_list(100)
    for note in notes:
        note["_id"] = str(note["_id"])
    return notes

# Get all notes by tag
@router.get("/tag/{tag}")
async def get_notes_by_tag(tag: str):
    notes = await notes_collection.find({"tags": tag}).to_list(100)
    for note in notes:
        note["_id"] = str(note["_id"])
    return notes
