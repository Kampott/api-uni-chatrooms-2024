from fastapi import HTTPException
import json
from pathlib import Path

chat_log_file = "../backend/app/models/chat_log.json"

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
