from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_analytics():
    return {"message": "Analytics endpoint is working"}
