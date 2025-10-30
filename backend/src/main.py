from fastapi import FastAPI
from .api.v1 import api_router
from .config.settings import config

def create_app() -> FastAPI:
    app = FastAPI(
        title=config.PROJECT_NAME,
        version="1.0.0"
    )
    
    # Include API routes
    app.include_router(api_router, prefix=config.API_V1_STR)
    
    @app.get("/")
    def read_root():
        return {"message": "Welcome to QoraTrader API"}
    
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "service": "QoraTrader API"}
    
    return app

app = create_app()

# For running with uvicorn directly
if __name__ == "main":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)