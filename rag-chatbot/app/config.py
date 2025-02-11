from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str = "mongodb://localhost:27017"
    weaviate_url: str
    weaviate_api_key: str
    cohere_api_key: str
    # model_name: str = "gpt-3.5-turbo"
    
    class Config:
        env_file = ".env"

settings = Settings()