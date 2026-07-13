from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import Base, engine
from database import models
from database.routes import router
from database.models import Lead, Company


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SalesGenie API")

# Allow Streamlit to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routes
app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "SalesGenie Backend Running Successfully"
    }