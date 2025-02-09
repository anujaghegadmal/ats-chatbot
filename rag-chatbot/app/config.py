from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str
    db_name: str
    algorithm: str
    secret_key: str
    weaviate_url: str
    openai_api_key: str
    wcd_api_key: str
    model_name: str = "gpt-3.5-turbo"
    
    
    class Config:
        env_file = ".env"

settings = Settings()