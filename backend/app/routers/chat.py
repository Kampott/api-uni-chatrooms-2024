from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.models.chat_log import save_message, get_chat_history
from typing import List, Dict
from datetime import datetime

router = APIRouter()

# Переменные для работы приложения
active_connections: Dict[str, List[WebSocket]] = {}

@router.websocket("/ws/chat")
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

@router.get("/api/chat/history/{room}")
async def get_chat_history_route(room: str):
    """
    Возвращает историю сообщений для определённой комнаты.
    """
    return get_chat_history(room)
