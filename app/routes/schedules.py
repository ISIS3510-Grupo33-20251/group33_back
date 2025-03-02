from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_schedules():
    return {"message": "List of schedules"}

