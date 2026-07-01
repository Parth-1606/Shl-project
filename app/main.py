import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.chat import router as chat_router

# Configure startup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="SHL Assessment Recommendation Agent",
        description="A stateless API that recommends, compares, and clarifies SHL tests based on user queries.",
        version="1.0.0"
    )

    # CORS settings - restrict this in a real production environment
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API Routers
    app.include_router(health_router, tags=["Health"])
    app.include_router(chat_router, tags=["Chat"])

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up SHL Recommendation Agent API...")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    # Allows running directly via `python app/main.py`
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
