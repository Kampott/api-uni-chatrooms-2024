from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from app.routers import chat  # Импортируем роутер для чата

app = FastAPI()

# CORS для поддержки запросов с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем запросы с любого источника
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

# Регистрируем маршруты из роутера chat
app.include_router(chat.router)

@app.get("/", response_class=HTMLResponse)
async def get_root():
    """
    Возвращает главную HTML-страницу чата.
    """
    template_path = os.path.join(os.path.dirname(__file__), "../../frontend/templates/index.html")
    with open(template_path, "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())
