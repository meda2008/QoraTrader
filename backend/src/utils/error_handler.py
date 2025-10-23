from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

class CustomException(Exception):
    """
    Custom exception class for application-specific errors
    """
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def init_error_handlers(app: FastAPI):
    """
    Initialize error handlers for the FastAPI application
    """
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.error(f"HTTP error {exc.status_code} for {request.url.path}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"message": exc.detail, "status_code": exc.status_code}},
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation error for {request.url.path}: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "message": "Input validation failed",
                    "status_code": 422,
                    "details": exc.errors()
                }
            },
        )
    
    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        logger.error(f"Custom error for {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"message": exc.message, "status_code": exc.status_code}},
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error for {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": "An unexpected error occurred",
                    "status_code": 500,
                    "details": str(exc) if app.debug else "Internal server error"
                }
            },
        )