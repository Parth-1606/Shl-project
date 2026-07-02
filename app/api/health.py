from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/health", summary="Health check endpoint")
async def health_check():
    """
    Returns the operational status of the service.
    """
    return {
        "status": "ok",
        "google_api_key_set": bool(os.getenv("GOOGLE_API_KEY")),
        "chroma_db_exists": os.path.exists(os.getenv("CHROMA_DB_DIR", "./chroma_db")),
    }
