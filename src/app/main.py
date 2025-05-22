import logging # Import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.app.core.config import settings
from src.app.api.endpoints import auth as auth_router, items as items_router # Import routers
from src.app.core.db import engine, Base # Import engine and Base
from src.app.core.logging_config import setup_logging # Import logging setup

# Apply logging configuration
setup_logging()
logger = logging.getLogger(__name__) # Get logger for main

# Instantiate the FastAPI application
app = FastAPI(title=settings.PROJECT_NAME)
logger.info("FastAPI application starting up...") # Log startup message

# Database table creation (for development)
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Custom error handling middleware
@app.middleware("http")
async def custom_http_exception_handler(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )
    except Exception as exc:
        # Handle any other unexpected errors
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error"},
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Include the authentication router
app.include_router(auth_router.router, prefix=settings.API_V1_STR, tags=["auth"])
# Include the items router
app.include_router(items_router.router, prefix=f"{settings.API_V1_STR}/items", tags=["items"])
