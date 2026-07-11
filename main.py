from fastapi import FastAPI
from database.connection import Base, engine
from database.models import Lead, Company
from modules.module1_leads import router as lead_router
from modules.module2_intelligence import router as intelligence_router

app = FastAPI(title="Salesgenie AI Backend")

Base.metadata.create_all(bind=engine)

app.include_router(lead_router)
app.include_router(intelligence_router)

@app.get("/")
def read_root():
    return {"message": "Salesgenie AI Backend is running successfully!"}