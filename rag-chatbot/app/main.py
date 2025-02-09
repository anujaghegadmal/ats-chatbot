from fastapi import FastAPI, HTTPException, Depends #status
from fastapi.security import OAuth2PasswordBearer
from app.routers import chat  # Import the chat router
from app.config import settings  # Import settings for MongoDB and JWT
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
from app.auth import get_current_user
# from app.schemas.chat import CreateChatRequest , CreateMessageRequest

# Initialize FastAPI app
app = FastAPI()

# Include the chat router
app.include_router(chat.router)

# Security and authentication setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class User(BaseModel):
    user_id: str
    user_name: str
    user_password: str

class UserInDB(User):
    hashed_password: str

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

# MongoDB connection setup
@app.on_event("startup")
async def startup_db():
    app.state.mongo_client = AsyncIOMotorClient(settings.mongo_uri)
    app.state.db = app.state.mongo_client[settings.db_name]
    app.state.users_collection = app.state.db.users
    app.state.chats_collection = app.state.db.chats
    app.state.messages_collection = app.state.db.messages
    print("Application startup: Initializing resources")

@app.on_event("shutdown")
async def shutdown_db():
    app.state.mongo_client.close()
    print("Application shutdown: Cleaning up resources")

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the ATS Chatbot API!"}

# User authentication functions
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def authenticate_user(user_id: str, password: str):
    user = await app.state.db.users.find_one({"user_id": user_id})
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

# User registration endpoint
@app.post("/register", response_model=User)
async def register(user: User):
    existing_user = await app.state.db.users.find_one({"user_id": user.user_id})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = get_password_hash(user.user_password)
    user_dict = user.dict()
    user_dict["hashed_password"] = hashed_password
    del user_dict["user_password"]

    await app.state.db.users.insert_one(user_dict)
    return user

# User login endpoint
# @app.post("/login", response_model=dict)
# async def login(user_id: str, password: str):
#     user = await authenticate_user(user_id, password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=30)  # Set your token expiration time
#     access_token = create_access_token(
#         data={"sub": user["user_id"]}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

# Chat and message endpoints (integrated from your previous code)
# @app.post("/chats", response_model=Chat)
# async def create_chat(chat_request: CreateChatRequest, current_user: User = Depends(get_current_user)):
#     if current_user["user_id"] != chat_request.user_id:
#         raise HTTPException(status_code=403, detail="Not authorized to create a chat for this user")

#     chat_id = str(ObjectId())  # Generate a unique chat ID
#     chat_data = {
#         "chat_id": chat_id,
#         "user_id": chat_request.user_id,
#         "created_at": datetime.utcnow(),
#         "updated_at": datetime.utcnow()
#     }
#     await app.state.chats_collection.insert_one(chat_data)
#     return chat_data

# @app.get("/chats/{user_id}", response_model=List[Chat])
# async def get_chats(user_id: str, current_user: User = Depends(get_current_user)):
#     if current_user["user_id"] != user_id:
#         raise HTTPException(status_code=403, detail="Not authorized to access chats for this user")

#     chats = await app.state.db.chats.find({"user_id": user_id}).to_list(None)
#     return chats

# @app.post("/chats/{chat_id}/messages", response_model=Message)
# async def add_message(
#     chat_id: str,
#     message_request: CreateMessageRequest,
#     current_user: User = Depends(get_current_user)
# ):
#     # Verify that the current user is authorized to add a message to this chat
#     if current_user["user_id"] != message_request.user_id:
#         raise HTTPException(status_code=403, detail="Not authorized to add a message to this chat")

#     # Check if the chat exists
#     chat = await app.state.db.chats.find_one({"chat_id": chat_id})
#     if not chat:
#         raise HTTPException(status_code=404, detail="Chat not found")

#     # Prepare the message data
#     message_data = {
#         "message_id": str(ObjectId()),
#         "chat_id": chat_id,
#         "user_id": message_request.user_id,
#         "role": message_request.role,
#         "content": message_request.content,
#         "timestamp": datetime.utcnow()
#     }

#     # Insert the message into the database
#     await app.state.db.messages.insert_one(message_data)

#     # Update the chat's 'updated_at' timestamp
#     await app.state.db.chats.update_one(
#         {"chat_id": chat_id},
#         {"$set": {"updated_at": datetime.utcnow()}}
#     )

#     return message_data

# @app.get("/chats/{chat_id}/messages", response_model=List[Message])
# async def get_messages(chat_id: str, current_user: User = Depends(get_current_user)):
#     chat = await app.state.db.chats.find_one({"chat_id": chat_id})
#     if not chat:
#         raise HTTPException(status_code=404, detail="Chat not found")
#     if current_user["user_id"] != chat["user_id"]:
#         raise HTTPException(status_code=403, detail="Not authorized to access this chat")

#     messages = await app.state.db.messages.find({"chat_id": chat_id}).to_list(None)
#     return messages

# @app.get("/chats/{chat_id}/full", response_model=ChatWithMessages)
# async def get_chat_with_messages(chat_id: str, current_user: User = Depends(get_current_user)):
#     chat = await app.state.db.chats.find_one({"chat_id": chat_id})
#     if not chat:
#         raise HTTPException(status_code=404, detail="Chat not found")
#     if current_user["user_id"] != chat["user_id"]:
#         raise HTTPException(status_code=403, detail="Not authorized to access this chat")

#     messages = await app.state.db.messages.find({"chat_id": chat_id}).to_list(None)
#     return {"chat": chat, "messages": messages}

# uvicorn app.main:app --reload