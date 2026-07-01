from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    CHROMA_DB_DIR: str = os.getenv("CHROMA_DB_DIR", "./chroma_db")
    CATALOG_JSON_PATH: str = os.getenv("CATALOG_JSON_PATH", "./app/catalog/data/catalog.json")
    MODEL_NAME: str = "gemini-2.5-flash"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
