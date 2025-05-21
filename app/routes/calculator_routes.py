from fastapi import APIRouter, HTTPException
from app.database import database
from app.models.calculator import CalculatorSubject
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/calculator", tags=["Calculator"])

calculator_collection = database["calculator"]

# Crear materia con su calculadora
@router.post("/", response_model=CalculatorSubject)
async def create_subject(subject: CalculatorSubject):
    subject_dict = subject.model_dump(by_alias=True, exclude={"subject_id"})
    subject_dict["created_date"] = datetime.utcnow()
    subject_dict["last_modified"] = datetime.utcnow()
    result = await calculator_collection.insert_one(subject_dict)
    subject_dict["_id"] = str(result.inserted_id)
    return subject_dict

# Obtener todas las materias de un usuario
@router.get("/user/{owner_id}")
async def get_subjects_by_user(owner_id: str):
    subjects = await calculator_collection.find({"owner_id": owner_id}).to_list(100)
    for subject in subjects:
        subject["_id"] = str(subject["_id"])
    return subjects

# Obtener una materia específica por ID
@router.get("/{subject_id}")
async def get_subject(subject_id: str):
    subject = await calculator_collection.find_one({"_id": ObjectId(subject_id)})
    if subject:
        subject["_id"] = str(subject["_id"])
        return subject
    raise HTTPException(status_code=404, detail="Subject not found")

# Actualizar una materia
@router.put("/{subject_id}")
async def update_subject(subject_id: str, updated_subject: CalculatorSubject):
    subject_dict = updated_subject.model_dump(exclude_unset=True, by_alias=True)
    subject_dict["last_modified"] = datetime.utcnow()
    result = await calculator_collection.update_one({"_id": ObjectId(subject_id)}, {"$set": subject_dict})
    if result.matched_count:
        return {"message": "Subject updated successfully"}
    raise HTTPException(status_code=404, detail="Subject not found")

# Eliminar una materia
@router.delete("/{subject_id}")
async def delete_subject(subject_id: str):
    result = await calculator_collection.delete_one({"_id": ObjectId(subject_id)})
    if result.deleted_count:
        return {"message": "Subject deleted successfully"}
    raise HTTPException(status_code=404, detail="Subject not found")
