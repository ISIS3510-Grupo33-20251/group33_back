#FAST API entry point
from fastapi import FastAPI
from app.routes.task_routes import router as task_router
from app.routes.user_routes import router as user_router
from app.routes.document_routes import router as document_router

app = FastAPI()

app.include_router(user_router)
app.include_router(task_router)
app.include_router(document_router)


@app.get("/")
def home():
    return {"message": "Welcome to the UniVerse API"}
