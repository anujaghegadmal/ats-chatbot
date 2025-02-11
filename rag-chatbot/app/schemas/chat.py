from pydantic import BaseModel
from datetime import datetime
from typing import List


class ChatRequest(BaseModel):
    message: str

class Chat(BaseModel):
    chat_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

class Message(BaseModel):
    message_id: str
    chat_id: str
    user_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class ChatWithMessages(BaseModel):
    chat: Chat
    messages: List[Message]

class CreateChatRequest(BaseModel):
    user_id: str

class CreateMessageRequest(BaseModel):
    user_id: str
    role: str  # "user" or "assistant"
    content: str