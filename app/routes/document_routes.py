from fastapi import APIRouter, HTTPException
from app.database import database
from app.models.document import Document
from bson import ObjectId

router = APIRouter(prefix="/documents", tags=["Documents"])

documents_collection = database["documents"]  # Reference to the "documents" collection

# Create a new document
@router.post("/", response_model=Document)
async def create_document(document: Document):
    document_dict = document.model_dump(by_alias=True, exclude={"document_id"})
    result = await documents_collection.insert_one(document_dict)

    # Set the created _id
    document_dict["_id"] = str(result.inserted_id)
    return document_dict

# Get all documents
@router.get("/")
async def get_documents():
    documents = await documents_collection.find().to_list(100)
    for document in documents:
        document["_id"] = str(document["_id"])  # Convert ObjectId to string
    return documents

# Get a single document by ID
@router.get("/{document_id}")
async def get_document(document_id: str):
    document = await documents_collection.find_one({"_id": ObjectId(document_id)})
    if document:
        document["_id"] = str(document["_id"])
        return document
    raise HTTPException(status_code=404, detail="Document not found")

# Update a document by ID
@router.put("/{document_id}")
async def update_document(document_id: str, updated_document: Document):
    document_dict = updated_document.model_dump(exclude_unset=True, by_alias=True)
    result = await documents_collection.update_one(
        {"_id": ObjectId(document_id)}, {"$set": document_dict}
    )
    if result.matched_count:
        return {"message": "Document updated successfully"}
    raise HTTPException(status_code=404, detail="Document not found")

# Delete a document by ID
@router.delete("/{document_id}")
async def delete_document(document_id: str):
    result = await documents_collection.delete_one({"_id": ObjectId(document_id)})
    if result.deleted_count:
        return {"message": "Document deleted successfully"}
    raise HTTPException(status_code=404, detail="Document not found")
