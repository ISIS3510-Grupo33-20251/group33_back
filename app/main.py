from fastapi import FastAPI
from app.routes import document_routes, user_routes, task_routes, team_routes, kanban_board_routes, schedule_routes, flashcard_deck_routes, reminder_routes

# Inicializar la aplicación FastAPI
app = FastAPI(title="Group33 Backend")

# Incluir las rutas
app.include_router(user_routes.router)
app.include_router(task_routes.router)
app.include_router(document_routes.router)
app.include_router(team_routes.router)
app.include_router(kanban_board_routes.router)
app.include_router(schedule_routes.router)
app.include_router(flashcard_deck_routes.router)
app.include_router(reminder_routes.router)

@app.get("/")
def root():
    return {"message": "🚀 API funcionando correctamente!"}
