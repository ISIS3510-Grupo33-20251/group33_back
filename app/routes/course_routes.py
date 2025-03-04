from fastapi import APIRouter, HTTPException
from app.database import database
from app.models.course import Course
from bson import ObjectId

router = APIRouter(prefix="/courses", tags=["Courses"])

courses_collection = database["courses"]
users_collection = database["users"]  # For checking members
documents_collection = database["documents"]  # For checking documents

# Create a new course
@router.post("/", response_model=Course)
async def create_course(course: Course):
    course_dict = course.model_dump(by_alias=True, exclude={"course_id"})
    result = await courses_collection.insert_one(course_dict)
    course_dict["_id"] = str(result.inserted_id)
    return course_dict

# Get all courses
@router.get("/")
async def get_courses():
    courses = await courses_collection.find().to_list(100)
    for course in courses:
        course["_id"] = str(course["_id"])
    return courses

# Get a single course by ID
@router.get("/{course_id}")
async def get_course(course_id: str):
    course = await courses_collection.find_one({"_id": ObjectId(course_id)})
    if course:
        course["_id"] = str(course["_id"])
        return course
    raise HTTPException(status_code=404, detail="Course not found")

# Update a course by ID
@router.put("/{course_id}")
async def update_course(course_id: str, updated_course: Course):
    course_dict = updated_course.model_dump(exclude_unset=True, by_alias=True)
    result = await courses_collection.update_one({"_id": ObjectId(course_id)}, {"$set": course_dict})
    if result.matched_count:
        return {"message": "Course updated successfully"}
    raise HTTPException(status_code=404, detail="Course not found")

# Delete a course by ID
@router.delete("/{course_id}")
async def delete_course(course_id: str):
    result = await courses_collection.delete_one({"_id": ObjectId(course_id)})
    if result.deleted_count:
        return {"message": "Course deleted successfully"}
    raise HTTPException(status_code=404, detail="Course not found")

# Get all members of a course
@router.get("/{course_id}/members")
async def get_course_members(course_id: str):
    course = await courses_collection.find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course.get("members", [])

# Add a member to a course
@router.post("/{course_id}/members/{user_id}")
async def add_member_to_course(course_id: str, user_id: str):
    result = await courses_collection.update_one({"_id": ObjectId(course_id)}, {"$addToSet": {"members": user_id}})
    if result.matched_count:
        return {"message": "Member added successfully"}
    raise HTTPException(status_code=404, detail="Course not found")

# Remove a member from a course
@router.delete("/{course_id}/members/{user_id}")
async def remove_member_from_course(course_id: str, user_id: str):
    result = await courses_collection.update_one({"_id": ObjectId(course_id)}, {"$pull": {"members": user_id}})
    if result.matched_count:
        return {"message": "Member removed successfully"}
    raise HTTPException(status_code=404, detail="Course not found")

# Get all documents of a course
@router.get("/{course_id}/documents")
async def get_course_documents(course_id: str):
    course = await courses_collection.find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course.get("documents", [])

# Add a document to a course
@router.post("/{course_id}/documents/{document_id}")
async def add_document_to_course(course_id: str, document_id: str):
    result = await courses_collection.update_one({"_id": ObjectId(course_id)}, {"$addToSet": {"documents": document_id}})
    if result.matched_count:
        return {"message": "Document added to course successfully"}
    raise HTTPException(status_code=404, detail="Course not found")

# Remove a document from a course
@router.delete("/{course_id}/documents/{document_id}")
async def remove_document_from_course(course_id: str, document_id: str):
    result = await courses_collection.update_one({"_id": ObjectId(course_id)}, {"$pull": {"documents": document_id}})
    if result.matched_count:
        return {"message": "Document removed from course successfully"}
    raise HTTPException(status_code=404, detail="Course not found")

# Get all notes of a course
@router.get("/{course_id}/notes")
async def get_course_notes(course_id: str):
    course = await courses_collection.find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course.get("notes", [])

# Add a note to a course
@router.post("/{course_id}/notes/{note_id}")
async def add_note_to_course(course_id: str, note_id: str):
    result = await courses_collection.update_one({"_id": ObjectId(course_id)}, {"$addToSet": {"notes": note_id}})
    if result.matched_count:
        return {"message": "Note added to course successfully"}
    raise HTTPException(status_code=404, detail="Course not found")

# Remove a note from a course
@router.delete("/{course_id}/notes/{note_id}")
async def remove_note_from_course(course_id: str, note_id: str):
    result = await courses_collection.update_one({"_id": ObjectId(course_id)}, {"$pull": {"notes": note_id}})
    if result.matched_count:
        return {"message": "Note removed from course successfully"}
    raise HTTPException(status_code=404, detail="Course not found")
