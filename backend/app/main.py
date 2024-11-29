from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from datetime import datetime
import os
import json

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

# Переменные для работы приложения
active_connections: Dict[str, List[WebSocket]] = {}
chat_log_file = "../backend/app/models/chat_log.json"


@app.get("/", response_class=HTMLResponse)
async def get_root():
    """
    Возвращает главную HTML-страницу чата.
    """
    template_path = os.path.join(os.path.dirname(__file__), "../../frontend/templates/index.html")
    with open(template_path, "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())


def save_message(room: str, username: str, message: str, image: str = None):
    """
    Сохраняет сообщение в лог-файл.
    """
    if not os.path.exists(chat_log_file):
        with open(chat_log_file, "w") as file:
            json.dump([], file)

    try:
        with open(chat_log_file, "r") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    logs.append({
        "room": room,
        "username": username,
        "message": message,
        "image": image,
        "timestamp": datetime.now().isoformat(),
    })

    with open(chat_log_file, "w") as file:
        json.dump(logs, file, indent=4)


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket для обработки сообщений чата.
    """
    await websocket.accept()
    room = None  # Текущая комната пользователя

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "join":
                room = data.get("room")
                if room:
                    if room not in active_connections:
                        active_connections[room] = []
                    if websocket not in active_connections[room]:
                        active_connections[room].append(websocket)
                    print(f"Клиент подключился к комнате: {room}")
            elif action == "message":
                # Проверяем данные сообщения
                room = data.get("room")
                username = data.get("username")
                message = data.get("message")

                if room and username and message:
                    print(f"Получено сообщение от {username} в комнате {room}: {message}")

                    # Сохраняем сообщение
                    save_message(room, username, message)

                    # Рассылаем сообщение всем пользователям комнаты
                    message_data = {
                        "room": room,
                        "username": username,
                        "message": message,
                        "timestamp": datetime.now().isoformat(),
                    }

                    disconnected = []
                    for connection in active_connections.get(room, []):
                        try:
                            await connection.send_json(message_data)
                        except WebSocketDisconnect:
                            disconnected.append(connection)

                    # Удаляем отключённых клиентов
                    for connection in disconnected:
                        active_connections[room].remove(connection)

    except WebSocketDisconnect:
        if room and websocket in active_connections.get(room, []):
            active_connections[room].remove(websocket)
            if not active_connections[room]:
                del active_connections[room]
        print(f"Клиент отключился от комнаты: {room}")



@app.get("/api/chat/history/{room}")
async def get_chat_history(room: str):
    """
    Возвращает историю сообщений для определённой комнаты.
    """
    try:
        with open(chat_log_file, "r") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    return [log for log in logs if log.get("room") == room]
