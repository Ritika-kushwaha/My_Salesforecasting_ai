
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str
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