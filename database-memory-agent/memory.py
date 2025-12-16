from config import memory_collection
from datetime import datetime
from typing import List

def store_chat_message(session_id: str, role: str, content: str) -> None:
    message = {
        "session_id": session_id,     # Unique identifier for the chat session
        "role": role,                 # Role of the sender (user or system)
        "content": content,           # Content of the message
        "timestamp": datetime.now(),  # Timestamp of when the message was sent
    }
    memory_collection.insert_one(message)

def retrieve_session_history(session_id: str) -> List:
    # Query the collection for messages with a specific "session_id" in ascending order
    cursor =  memory_collection.find({"session_id": session_id}).sort("timestamp", 1)

    # Iterate through the cursor and return a JSON object with the message role and content
    if cursor:
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in cursor]
    else:
        messages = []
    return messages


