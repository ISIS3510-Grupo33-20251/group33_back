from fastapi import FastAPI, Request
from app.routes import document_routes, user_routes, task_routes, team_routes, kanban_board_routes, schedule_routes, flashcard_deck_routes, reminder_routes, calculator_routes, course_routes, friend_request_routes, note_routes, meeting_routes

import logging


logging.basicConfig(
    filename="logs_app.log", 
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s", 
)


# Inicializar la aplicación FastAPI
app = FastAPI(title="Group33 Backend")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    response = await call_next(request)
    logging.info(f"IP: {request.client.host} - Method: {request.method} - URL: {request.url} - Body: {True if body else False} Response: {response.status_code}")
    return response

# Incluir las rutas
app.include_router(user_routes.router)
app.include_router(task_routes.router)
app.include_router(document_routes.router)
app.include_router(team_routes.router)
app.include_router(kanban_board_routes.router)
app.include_router(schedule_routes.router)
app.include_router(flashcard_deck_routes.router)
app.include_router(reminder_routes.router)
app.include_router(course_routes.router)
app.include_router(friend_request_routes.router)
app.include_router(note_routes.router)
app.include_router(meeting_routes.router)
app.include_router(calculator_routes.router)


@app.get("/")
def root():
    return {"message": "🚀 API funcionando correctamente!"}


from charts import generar_graficos
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")
@app.get("/dashboard")
async def dashboard(request: Request):
    graficos = generar_graficos()
    return templates.TemplateResponse("dashboard.html", {"request": request, "graficos": graficos})


