import json
import os
from datetime import datetime

chat_log_file = "../backend/app/models/chat_log.json"

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

def get_chat_history(room: str):
    """
    Возвращает историю сообщений для определённой комнаты.
    """
    try:
        with open(chat_log_file, "r") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    return [log for log in logs if log.get("room") == room]
