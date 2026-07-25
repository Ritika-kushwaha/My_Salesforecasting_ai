from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from database.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
<<<<<<< Updated upstream
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    company = Column(String(100))
    industry = Column(String(100))
=======
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Use 'company' and 'name' to match your database schema
    name = Column(String(100), nullable=True)
    company = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(30), nullable=True)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    revenue = Column(String(50), nullable=True)
    lead_score = Column(Integer, default=0)
    priority = Column(String(20), default="Medium")
>>>>>>> Stashed changes
    status = Column(String(30), default="New")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), nullable=False)
    website = Column(String(255))
    industry = Column(String(100))
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())