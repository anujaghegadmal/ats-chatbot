from pydantic import BaseModel

class ChatRequest(BaseModel):
    conversation_id: str
    message: str
    user_id: str

class ChatResponse(BaseModel):
    response: str
    sources: list[str] = []
