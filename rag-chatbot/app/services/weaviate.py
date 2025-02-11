import weaviate
from app.config import settings
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

async def connect_to_weaviate():
    try:
      
        client = weaviate.Client(
            url=settings.weaviate_url,
            auth_client_secret=weaviate.auth.AuthApiKey(api_key=settings.weaviate_api_key),
)
        # Check if the connection is successful by calling the .is_ready() method
        if not client.is_ready():
            raise Exception("Weaviate is not ready.")
        
        # Log success message
        logger.info("Successfully connected to Weaviate.")
        
        return client
    except Exception as e:
        logger.error(f"Error connecting to Weaviate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error connecting to Weaviate: {str(e)}")