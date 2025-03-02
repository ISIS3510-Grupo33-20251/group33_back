from fastapi import FastAPI
from app.routes import users, schedules, meetings, reminders, analytics
from app.database import Base, engine

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Inicializar la aplicación FastAPI
app = FastAPI(title="Group33 Backend", version="1.0")

# Incluir las rutas
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(schedules.router, prefix="/schedules", tags=["Schedules"])
app.include_router(meetings.router, prefix="/meetings", tags=["Meetings"])
app.include_router(reminders.router, prefix="/reminders", tags=["Reminders"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

@app.get("/")
def root():
    return {"message": "🚀 API funcionando correctamente!"}
