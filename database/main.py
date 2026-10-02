import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import Base, engine
from database.routes import router as api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables AFTER uvicorn has bound the port
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully.")
    except Exception as e:
        logger.error(f"Database startup error (non-fatal): {e}")
    yield
    # Shutdown (nothing needed)


# Initialize FastAPI Application
app = FastAPI(
    title="SalesGenie AI Backend API",
    description="REST API for B2B Sales Intelligence, Lead Scoring, and AI Generation",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Endpoints Router
app.include_router(api_router)


# Root Health Check — must respond instantly (no DB call)
@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "SalesGenie AI Backend",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    uvicorn.run("database.main:app", host="127.0.0.1", port=8000, reload=True)