from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log incoming requests
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log the incoming request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # Calculate process time
        process_time = time.time() - start_time
        
        # Add process time to response headers
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log the response
        logger.info(f"Response: {response.status_code} in {process_time:.4f}s")
        
        return response

def setup_middleware(app: FastAPI):
    """
    Setup middleware for the FastAPI application
    """
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Expose headers that clients can access
        expose_headers=["X-Process-Time"]
    )
    
    # GZip compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Request logging middleware
    app.add_middleware(RequestLoggingMiddleware)