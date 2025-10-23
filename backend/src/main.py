from fastapi import FastAPI
from src.api.v1 import api_router
from src.config.settings import settings
from src.utils.logging_config import setup_logging
from src.utils.error_handler import init_error_handlers
from src.utils.middleware import setup_middleware
import uvicorn
import os

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application
    """
    # Setup logging
    setup_logging()
    
    # Create FastAPI instance
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        openapi_url=settings.OPENAPI_URL,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Initialize error handlers
    init_error_handlers(app)
    
    # Include API routers
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "timestamp": "2025-10-22T10:30:00Z"}
    
    return app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG_MODE
    )