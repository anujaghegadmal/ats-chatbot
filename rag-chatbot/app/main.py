from fastapi import FastAPI, HTTPException, Depends , status
from fastapi.security import OAuth2PasswordBearer
from app.routers import chat
from app.config import settings
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
@app.post("/login", response_model=dict)
async def login(user_id: str, password: str):
    user = await authenticate_user(user_id, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)  # Set your token expiration time
    access_token = create_access_token(
        data={"sub": user["user_id"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

