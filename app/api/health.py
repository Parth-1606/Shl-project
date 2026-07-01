from fastapi import APIRouter

router = APIRouter()

@router.get("/health", summary="Health check endpoint")
async def health_check():
    """
    Returns the operational status of the service.
    """
    return {"status": "ok"}
