
from pydantic import BaseModel

class LeadCreate(BaseModel):
    name: str
    email: str
    phone: str
    company: str
    industry: str
class LeadUpdate(BaseModel):
    name: str
    email: str
    phone: str
    company: str
    industry: str
    status: str

class LeadScoreRequest(BaseModel):
    company: str
    industry: str