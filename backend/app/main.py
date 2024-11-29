from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from datetime import datetime
from datetime import timedelta
from fastapi.responses import JSONResponse
import json
import os

app = FastAPI()

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

# Корневой маршрут для рендера index.html
@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = os.path.join(os.path.dirname(__file__), "../../frontend/templates/index.html")
    with open(template_path, "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())

# Лог чата
chat_log_file = "../backend/app/models/chat_log.json"

def save_message(username, message):
    if not os.path.exists(chat_log_file):
        with open(chat_log_file, "w") as file:
            json.dump([], file)

    try:
        with open(chat_log_file, "r") as file:
            logs = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        logs = []

    # Добавляем сообщение с временной меткой
    logs.append({
        "username": username,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })

    with open(chat_log_file, "w") as file:
        json.dump(logs, file, indent=4)

def get_recent_messages(hours=2):
    try:
        with open(chat_log_file, "r") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    # Фильтруем сообщения по временной метке
    two_hours_ago = datetime.now() - timedelta(hours=hours)
    return [log for log in logs if datetime.fromisoformat(log["timestamp"]) > two_hours_ago]
# WebSocket для чата
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            message = {
                "username": data["username"],
                "message": data["message"],
                "timestamp": datetime.now().isoformat()
            }
            save_message(data["username"], data["message"])
            await websocket.send_json(message)
    except WebSocketDisconnect:
        print("Клиент отключился")

@app.get("/api/chat/history")
async def get_chat_history():
    recent_messages = get_recent_messages()
    return JSONResponse(content=recent_messages)