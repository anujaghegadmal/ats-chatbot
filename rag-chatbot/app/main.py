from fastapi import FastAPI
from app.routers import chat
from app.config import settings
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

app.include_router(chat.router)

@app.on_event("startup")
async def startup_db():
    app.state.mongo_client = AsyncIOMotorClient(settings.mongo_uri)
    # app.state.db = app.state.mongo_client[settings.db_name]
    print("Application startup: Initializing resources")

@app.on_event("shutdown")
async def shutdown_db():
    app.state.mongo_client.close()
    print("Application shutdown: Cleaning up resources")

@app.get("/")
async def read_root():
    return {"Hello World!"}