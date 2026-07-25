from database.database import Base
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


# Ensure Campaign model is defined
class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)

    title = Column(String(150), nullable=True)
    subject = Column(String(200), nullable=True)
    body = Column(Text, nullable=True)
    target_industry = Column(String(100), nullable=True)
    status = Column(String(50), default="Draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="Sales Rep")
    department = Column(String(50), default="Sales")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    company_name = Column(String(100), nullable=False)
    industry = Column(String(100))
    contact_name = Column(String(100))
    email = Column(String(100), nullable=False)
    phone = Column(String(30))
    lead_status = Column(String(30), default="New")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CompanyInsight(Base):
    __tablename__ = "company_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)

    company_name = Column(String(100), nullable=False)
    website = Column(String(255))
    industry = Column(String(100))
    business_needs = Column(Text)
    opportunities = Column(Text)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())


class LeadScore(Base):
    __tablename__ = "lead_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)

    lead_score = Column(Integer, default=0)
    conversion_probability = Column(String(20), default="0%")
    priority = Column(String(20), default="Medium")
    generated_at = Column(DateTime(timezone=True), server_default=func.now())


class OutreachCampaign(Base):
    __tablename__ = "outreach_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)

    email_subject = Column(String(200))
    email_content = Column(Text)
    campaign_status = Column(String(30), default="Draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SalesInteraction(Base):
    __tablename__ = "sales_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)

    sender = Column(String(50))  # 'User' or 'AI Assistant'
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    company_name = Column(String(100), nullable=False)
    website = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())