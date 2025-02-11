# app/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

# Initialize MongoDB client
client = AsyncIOMotorClient(settings.mongo_uri)

# Get the database
db = client[settings.db_name]
users_collection = db.users
chats_collection = db.chats
messages_collection = db.messages