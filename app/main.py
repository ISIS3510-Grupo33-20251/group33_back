from fastapi import FastAPI
from app.routes import schedules, meetings, reminders, analytics, document_routes, user_routes, task_routes

# Inicializar la aplicación FastAPI
app = FastAPI(title="Group33 Backend")

# Incluir las rutas
app.include_router(schedules.router, prefix="/schedules", tags=["Schedules"])
app.include_router(meetings.router, prefix="/meetings", tags=["Meetings"])
app.include_router(reminders.router, prefix="/reminders", tags=["Reminders"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(user_routes.router)
app.include_router(task_routes.router)
app.include_router(document_routes.router)

@app.get("/")
def root():
    return {"message": "🚀 API funcionando correctamente!"}
