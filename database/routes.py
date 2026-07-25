import math
import os
import re
import traceback
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from google import genai
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import Company, Conversation, Lead, User

router = APIRouter()

# Initialize Google Gemini Client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def clean_json_response(text: str) -> dict:
    """Utility to clean Markdown code block formatting from Gemini responses."""
    import json

    cleaned = re.sub(r"```json\s*", "", text)
    cleaned = re.sub(r"```\s*$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        return {}


# =====================================================================
# AUTHENTICATION ENDPOINTS
# =====================================================================


@router.post("/signup")
def signup(data: dict, db: Session = Depends(get_db)):
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    name = data.get("name", "").strip()

    if not email or not password:
        raise HTTPException(
            status_code=400, detail="Email and password are required."
        )

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=400, detail="User with this email already exists."
        )

    new_user = User(name=name, email=email, password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user": {"id": new_user.id, "name": new_user.name, "email": new_user.email},
    }


@router.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    user = (
        db.query(User)
        .filter(User.email == email, User.password == password)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=401, detail="Invalid email or password."
        )

    return {
        "message": "Login successful",
        "user": {"id": user.id, "name": user.name, "email": user.email},
    }


# =====================================================================
# LEAD MANAGEMENT ENDPOINTS
# =====================================================================


# --- GET ALL LEADS (No user_id filtering) ---
@router.get("/leads")
def get_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    result = []
    for lead in leads:
        result.append(
            {
                "id": lead.id,
                "name": getattr(lead, "name", None) or getattr(lead, "contact_name", "N/A"),
                "company": getattr(lead, "company", None) or getattr(lead, "company_name", "N/A"),
                "email": lead.email,
                "phone": lead.phone,
                "industry": lead.industry,
                "company_size": lead.company_size,
                "revenue": str(lead.revenue),
                "lead_score": lead.lead_score,
                "priority": lead.priority,
                "status": getattr(lead, "status", None) or getattr(lead, "lead_status", "New"),
                "created_at": lead.created_at.isoformat() if lead.created_at else None,
            }
        )
    return result


# --- DASHBOARD METRICS (No user_id filtering) ---
@router.get("/dashboard")
def get_dashboard_data(db: Session = Depends(get_db)):
    query_leads = db.query(Lead)
    total_leads = query_leads.count()

    high_priority_count = query_leads.filter(func.lower(Lead.priority) == "high").count()

    qualified_count = 0
    try:
        qualified_count = query_leads.filter(func.lower(Lead.status) == "qualified").count()
    except Exception:
        qualified_count = 0

    conversion_rate = (
        round((qualified_count / total_leads) * 100, 1) if total_leads > 0 else 0.0
    )

    return {
        "total_leads": total_leads,
        "high_priority_leads": high_priority_count,
        "qualified_leads": qualified_count,
        "conversion_rate": conversion_rate,
    }


@router.delete("/leads/{lead_id}")
def delete_lead(lead_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    try:
        # 1. Fetch target lead for the user
        lead = (
            db.query(Lead)
            .filter(Lead.id == lead_id, Lead.user_id == user_id)
            .first()
        )
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        # 2. Delete linked conversations first
        db.query(Conversation).filter(
            Conversation.lead_id == lead_id
        ).delete(synchronize_session=False)
        db.commit()

        # 3. Delete the lead
        db.delete(lead)
        db.commit()

        return {"message": f"Lead {lead_id} successfully deleted"}

    except HTTPException as http_ex:
        db.rollback()
        raise http_ex

    except Exception as e:
        db.rollback()
        # Print exact traceback in Uvicorn terminal for debugging
        print("\n--- DELETE ERROR TRACEBACK ---")
        traceback.print_exc()
        print("------------------------------\n")

        raise HTTPException(
            status_code=500, detail=f"Database deletion error: {str(e)}"
        )
    
@router.delete("/leads/{lead_id}")
def delete_lead(lead_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == user_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        db.delete(lead)
        db.commit()
        return {"message": f"Lead {lead_id} deleted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Database deletion error: {str(e)}"
        )

@router.post("/leads/bulk")
def create_leads_bulk(
    leads: List[dict], user_id: int = 1, db: Session = Depends(get_db)
):
    try:
        created_count = 0

        # Fetch existing emails to avoid insertion failures if uniquely constrained
        existing_emails = {
            l[0].lower()
            for l in db.query(Lead.email).filter(Lead.user_id == user_id).all()
            if l[0]
        }

        for lead in leads:

            def clean_str(val, default=""):
                if val is None or (isinstance(val, float) and math.isnan(val)):
                    return default
                return str(val).strip()

            company_val = clean_str(
                lead.get("company") or lead.get("company_name"),
                "Unknown Company",
            )
            name_val = clean_str(
                lead.get("name") or lead.get("contact_name"), "Unknown Contact"
            )
            email_val = clean_str(
                lead.get("email"),
                f"contact@{company_val.lower().replace(' ', '')}.com",
            ).lower()

            # Skip if lead already exists
            if email_val in existing_emails:
                continue

            # Safely handle numeric or string values for revenue
            raw_rev = lead.get("revenue")
            rev_val = "N/A"
            if raw_rev is not None and not (
                isinstance(raw_rev, float) and math.isnan(raw_rev)
            ):
                rev_val = str(raw_rev).strip()

            db_lead = Lead(
                user_id=user_id,
                name=name_val,
                company=company_val,
                email=email_val,
                phone=clean_str(lead.get("phone"), "N/A"),
                industry=clean_str(lead.get("industry"), "General"),
                company_size=clean_str(lead.get("company_size"), "1-10"),
                revenue=rev_val,
                priority=clean_str(lead.get("priority"), "Medium"),
                status=clean_str(lead.get("status"), "New"),
            )
            db.add(db_lead)
            existing_emails.add(email_val)
            created_count += 1

        db.commit()
        return {"message": f"Successfully imported {created_count} leads!"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database import error: {str(e)}"
        )


# =====================================================================
# COMPANY INTELLIGENCE (GEMINI AI)
# =====================================================================


@router.post("/analyze-company")
def analyze_company(
    data: dict, user_id: int = 1, db: Session = Depends(get_db)
):
    company_name = data.get("company", "").strip()
    website = data.get("website", "").strip() or "Not Provided"
    industry = data.get("industry", "").strip() or "General Business"

    if not company_name or len(company_name) < 2:
        raise HTTPException(
            status_code=400, detail="A valid Company Name is required."
        )

    if not client:
        # Structured fallback if GEMINI_API_KEY is not configured
        result = {
            "company": company_name,
            "industry": industry,
            "lead_score": 75,
            "grade": "B",
            "company_summary": f"{company_name} operates in the {industry} sector.",
            "sales_opportunity": "Target core decision-makers for process optimization.",
            "recommended_sales_approach": "Send personalized email highlighting ROI value.",
        }
    else:
        prompt = f"""
You are an expert sales intelligence analyst. Analyze this company for B2B sales potential:

Company Name: {company_name}
Website: {website}
Industry: {industry}

Return ONLY valid JSON in this exact structure:
{{
  "company": "{company_name}",
  "industry": "{industry}",
  "lead_score": 85,
  "grade": "A",
  "company_summary": "Comprehensive overview of {company_name}...",
  "sales_opportunity": "Key pain points and expansion opportunities...",
  "recommended_sales_approach": "Actionable outreach strategy..."
}}
"""
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            result = clean_json_response(response.text)
        except Exception as e:
            result = {
                "company": company_name,
                "industry": industry,
                "lead_score": 70,
                "grade": "B",
                "company_summary": f"Research profile created for {company_name}.",
                "sales_opportunity": "Schedule discovery call to evaluate pain points.",
                "recommended_sales_approach": "Introductory outreach campaign.",
            }

    # Record or update company in Database
    existing = (
        db.query(Company)
        .filter(
            Company.company_name == company_name, Company.user_id == user_id
        )
        .first()
    )
    if not existing:
        new_comp = Company(
            user_id=user_id,
            company_name=company_name,
            website=website,
            industry=industry,
            description=result.get("company_summary", ""),
        )
        db.add(new_comp)
        db.commit()

    return result


# =====================================================================
# DASHBOARD METRICS
# =====================================================================


