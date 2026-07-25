import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import Base, engine
from database.routes import router as api_router

# 1. Automatically create tables in PostgreSQL on startup if they don't exist
Base.metadata.create_all(bind=engine)

# 2. Initialize FastAPI Application
app = FastAPI(
    title="SalesGenie AI Backend API",
    description="REST API for B2B Sales Intelligence, Lead Scoring, and AI Generation",
    version="1.0.0",
)

# 3. Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production to restrict domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Include API Endpoints Router
app.include_router(api_router)


# Root Health Check
@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "SalesGenie AI Backend",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    uvicorn.run("database.main:app", host="127.0.0.1", port=8000, reload=True)