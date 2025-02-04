from beanie import Document
from datetime import datetime
from pydantic import ConfigDict

class Message(Document):
    content: str
    sender: str
    timestamp: datetime = datetime.now()
    conversation_id: str

    model_config = ConfigDict(from_attributes=True)  # Need to replace class Config

    class Settings:
        name = "messages"