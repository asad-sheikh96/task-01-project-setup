
from datetime import datetime, timezone

messages = []
next_message_id = 1


def create_message(role: str, content: str):
    global next_message_id

    message = {
        "id": next_message_id,
        "role": role,
        "content": content,
        "created_at": datetime.now(timezone.utc)
    }

    messages.append(message)
    next_message_id += 1

    return message


def get_message(message_id: int):
    for message in messages:
        if message["id"] == message_id:
            return message
    return None


def update_message(message_id: int, content: str):
    message = get_message(message_id)

    if message is None:
        return None

    message["content"] = content
    return message


def delete_message(message_id: int):
    message = get_message(message_id)

    if message is None:
        return False

    messages.remove(message)
    return True
