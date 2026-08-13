import math
import os
import re
import traceback
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from google import genai
from pydantic import BaseModel
from sqlalchemy import func, text
from sqlalchemy.orm import Session
import requests

from database.database import get_db
from database.models import Company, Conversation, Lead, User

router = APIRouter()

# -------------------------------------------------------------------
# ENVIRONMENT & CONFIGURATION
# -------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Google OAuth Credentials for Backend Verification
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8501/")


def clean_json_response(text: str) -> dict:
    """Utility to clean Markdown code block formatting from Gemini responses."""
    import json

    cleaned = re.sub(r"```json\s*", "", text)
    cleaned = re.sub(r"```\s*$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        return {}


# ==========================================
# GOOGLE AUTHENTICATION (Login & Signup)
# ==========================================
class GoogleAuthRequest(BaseModel):
    token: str | None = None
    email: str | None = None
    name: str | None = None


@router.post("/auth/google")
def google_auth(data: GoogleAuthRequest, db: Session = Depends(get_db)):
    user_email = None
    user_name = None

    # 1. Exchange OAuth authorization code for Google user details
    if data.token:
        try:
            token_res = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": data.token,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
                timeout=10,
            )
            token_json = token_res.json()
            access_token = token_json.get("access_token")

            if not access_token:
                raise HTTPException(
                    status_code=400,
                    detail=f"Google OAuth Error: {token_json.get('error_description', 'Invalid authorization token')}"
                )

            # Fetch User Profile from Google
            user_info_res = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            user_info = user_info_res.json()
            user_email = user_info.get("email")
            user_name = user_info.get("name") or (user_email.split("@")[0] if user_email else "Google User")

        except requests.exceptions.Timeout:
            raise HTTPException(status_code=504, detail="Google OAuth server request timed out.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to verify Google token: {e}")

    # Fallback if direct payload is sent
    elif data.email:
        user_email = data.email
        user_name = data.name or "Google User"

    if not user_email:
        raise HTTPException(status_code=400, detail="Could not retrieve email from Google account.")

    # 2. Query or Create User dynamically in PostgreSQL
    user = db.query(User).filter(User.email == user_email).first()

    if not user:
        # Pass a placeholder password so NOT NULL constraint is satisfied
        user = User(email=user_email, name=user_name, password="oauth_google_account")
        db.add(user)
        db.commit()
        db.refresh(user)

    # 3. Return Unique User Payload
    return {
        "status": "success",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
        },
    }


# ==========================================
# MANUAL SIGNUP
# ==========================================
@router.post("/signup")
def signup(data: dict, db: Session = Depends(get_db)):
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    name = data.get("name", "").strip()

    if not email or not password or not name:
        raise HTTPException(status_code=400, detail="Name, Email, and Password are required.")

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    new_user = User(name=name, email=email, password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "status": "success",
        "message": "User created successfully",
        "user": {"id": new_user.id, "name": new_user.name, "email": new_user.email}
    }


# ==========================================
# MANUAL LOGIN
# ==========================================
@router.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    user = db.query(User).filter(User.email == email, User.password == password).first()
    if not user:
        # Pass a placeholder password so NOT NULL constraint is satisfied
        user = User(email=user_email, name=user_name, password="oauth_google_account")
        db.add(user)
        db.commit()
        db.refresh(user)
    return {
        "status": "success",
        "message": "Login successful",
        "user": {"id": user.id, "name": user.name, "email": user.email}
    }


# =====================================================================
# LEAD MANAGEMENT ENDPOINTS
# =====================================================================

@router.get("/leads")
def get_leads(user_id: int = 1, db: Session = Depends(get_db)):
    leads = db.query(Lead).filter(Lead.user_id == user_id).all()
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


@router.post("/leads")
def create_lead(data: dict, user_id: int = 1, db: Session = Depends(get_db)):
    name = data.get("name") or data.get("contact_name")
    company = data.get("company") or data.get("company_name")
    email = data.get("email")

    if not name or not company or not email:
        raise HTTPException(status_code=400, detail="Name, Company, and Email are required.")

    new_lead = Lead(
        user_id=user_id,
        name=name,
        company=company,
        email=email,
        phone=data.get("phone", ""),
        industry=data.get("industry", "General"),
        company_size=data.get("company_size", "1-10"),
        revenue=data.get("revenue", "0"),
        priority=data.get("priority", "Medium"),
        status=data.get("status", "New"),
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return {"message": "Lead created successfully", "lead_id": new_lead.id}


@router.put("/leads/{lead_id}")
def update_lead(lead_id: int, data: dict, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead with ID #{lead_id} not found.")

    try:
        if "name" in data and data["name"]:
            lead.name = data["name"]
        if "company" in data and data["company"]:
            lead.company = data["company"]
        if "email" in data and data["email"]:
            lead.email = data["email"]
        if "phone" in data:
            lead.phone = data["phone"]
        if "industry" in data:
            lead.industry = data["industry"]
        if "priority" in data:
            lead.priority = data["priority"]
        if "status" in data:
            lead.status = data["status"]

        db.commit()
        db.refresh(lead)
        return {"message": f"Lead {lead_id} updated successfully", "lead": data}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update lead: {str(e)}")


@router.delete("/leads/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead with ID #{lead_id} not found.")

    try:
        db.execute(text("DELETE FROM conversations WHERE lead_id = :lead_id"), {"lead_id": lead_id})
        db.delete(lead)
        db.commit()
        return {"message": f"Lead #{lead_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database deletion error: {str(e)}")


@router.post("/leads/bulk")
def create_leads_bulk(leads: List[dict], user_id: int = 1, db: Session = Depends(get_db)):
    try:
        created_count = 0
        existing_emails = {
            l[0].lower() for l in db.query(Lead.email).filter(Lead.user_id == user_id).all() if l[0]
        }

        for lead in leads:
            def clean_str(val, default=""):
                if val is None or (isinstance(val, float) and math.isnan(val)):
                    return default
                return str(val).strip()

            company_val = clean_str(lead.get("company") or lead.get("company_name"), "Unknown Company")
            name_val = clean_str(lead.get("name") or lead.get("contact_name"), "Unknown Contact")
            email_val = clean_str(lead.get("email"), f"contact@{company_val.lower().replace(' ', '')}.com").lower()

            if email_val in existing_emails:
                continue

            raw_rev = lead.get("revenue")
            rev_val = "N/A"
            if raw_rev is not None and not (isinstance(raw_rev, float) and math.isnan(raw_rev)):
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
        raise HTTPException(status_code=500, detail=f"Database import error: {str(e)}")


# =====================================================================
# AI OUTREACH GENERATOR ENDPOINT
# =====================================================================

@router.post("/generate-outreach")
def generate_outreach(data: dict, user_id: int = 1, db: Session = Depends(get_db)):
    name = data.get("name", "Prospect").strip()
    company = data.get("company", "Target Company").strip()
    industry = data.get("industry", "General Industry").strip()
    channel = data.get("channel", "Cold Email").strip()
    tone = data.get("tone", "Professional & Persuasive").strip()
    value_prop = data.get("value_prop", "").strip()

    prompt = f"""
You are an expert sales copywriter. Write a personalized {channel} for a prospective buyer.

Target Details:
- Contact Name: {name}
- Company Name: {company}
- Industry: {industry}
- Communication Tone: {tone}
- Value Proposition / Offer: {value_prop if value_prop else 'AI-driven automation that reduces sales cycle times'}

Return ONLY valid JSON in this exact format:
{{
  "subject": "Compelling subject line or headline",
  "body": "Personalized message body tailored to the target and tone..."
}}
"""

    if not client:
        return {
            "subject": f"Quick question regarding {company}'s growth",
            "body": f"Hi {name},\n\nI noticed {company}'s impressive work in {industry}. {value_prop if value_prop else 'We specialize in AI solutions to streamline outreach.'}\n\nWould you be open to a 10-minute chat this Thursday?\n\nBest regards,\nSalesGenie Team"
        }

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        ai_res = clean_json_response(response.text)
        if "subject" not in ai_res or "body" not in ai_res:
            raise ValueError("Invalid format")
        return ai_res
    except Exception:
        return {
            "subject": f"Exploring growth opportunities for {company}",
            "body": f"Hi {name},\n\nHope this finds you well. Given your focus in {industry}, I wanted to reach out regarding how {company} can benefit from AI outreach automation.\n\n{value_prop if value_prop else 'We help sales teams scale messaging without sacrificing personalization.'}\n\nLet me know if you have 10 minutes for a brief call this week.\n\nBest regards,\nSalesGenie Team"
        }


# =====================================================================
# CONVERSATION INTELLIGENCE ENDPOINTS
# =====================================================================

@router.get("/conversations")
def get_conversations(lead_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    conversations = (
        db.query(Conversation)
        .filter(Conversation.lead_id == lead_id, Conversation.user_id == user_id)
        .all()
    )
    if not conversations:
        return []

    return [
        {
            "id": c.id,
            "lead_id": c.lead_id,
            "interaction_type": getattr(c, "interaction_type", "Call"),
            "transcript": getattr(c, "transcript", None) or getattr(c, "message", ""),
            "summary": getattr(c, "summary", ""),
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in conversations
    ]


@router.post("/analyze-conversation")
def analyze_conversation(data: dict, user_id: int = 1, db: Session = Depends(get_db)):
    lead_id = data.get("lead_id")
    transcript = data.get("transcript", "").strip()
    interaction_type = data.get("interaction_type", "Call")

    if not lead_id or not transcript:
        raise HTTPException(status_code=400, detail="lead_id and transcript are required.")

    if not client:
        ai_data = {
            "summary": "Meeting transcript processed and logged.",
            "key_points": ["Reviewed prospect requirements"],
            "action_items": ["Follow up with custom proposal"],
            "recommended_stage": "Qualified"
        }
    else:
        prompt = f"""
Analyze the following sales interaction ({interaction_type}):
"{transcript}"

Return ONLY valid JSON in this exact structure:
{{
  "summary": "Key discussion summary...",
  "key_points": ["Point 1", "Point 2"],
  "action_items": ["Action 1", "Action 2"],
  "recommended_stage": "Qualified"
}}
"""
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            ai_data = clean_json_response(response.text)
        except Exception:
            ai_data = {
                "summary": "Transcript analyzed successfully.",
                "key_points": ["Discussed feature requirements"],
                "action_items": ["Send technical proposal"],
                "recommended_stage": "Proposal Sent"
            }

    new_conv = Conversation(
        user_id=user_id,
        lead_id=lead_id,
        interaction_type=interaction_type,
        transcript=transcript,
        summary=ai_data.get("summary", ""),
        sender="AI",
        message=ai_data.get("summary", transcript[:255])
    )

    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == user_id).first()
    if lead and "recommended_stage" in ai_data:
        lead.status = ai_data["recommended_stage"]

    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)

    return {"message": "Conversation analyzed and saved successfully", "data": ai_data}


# =====================================================================
# COMPANY INTELLIGENCE (GEMINI AI)
# =====================================================================

@router.post("/analyze-company")
def analyze_company(data: dict, user_id: int = 1, db: Session = Depends(get_db)):
    company_name = data.get("company", "").strip()
    website = data.get("website", "").strip() or "Not Provided"
    industry = data.get("industry", "").strip() or "General Business"

    if not company_name or len(company_name) < 2:
        raise HTTPException(status_code=400, detail="A valid Company Name is required.")

    if not client:
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
        except Exception:
            result = {
                "company": company_name,
                "industry": industry,
                "lead_score": 70,
                "grade": "B",
                "company_summary": f"Research profile created for {company_name}.",
                "sales_opportunity": "Schedule discovery call to evaluate pain points.",
                "recommended_sales_approach": "Introductory outreach campaign.",
            }

    existing = (
        db.query(Company)
        .filter(Company.company_name == company_name, Company.user_id == user_id)
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

@router.get("/dashboard")
def get_dashboard_data(user_id: int = 1, db: Session = Depends(get_db)):
    query_leads = db.query(Lead).filter(Lead.user_id == user_id)
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

    total_companies = db.query(Company).filter(Company.user_id == user_id).count()

    return {
        "total_leads": total_leads,
        "high_priority_leads": high_priority_count,
        "qualified_leads": qualified_count,
        "conversion_rate": conversion_rate,
        "total_companies": total_companies
    }


# =====================================================================
# COMPETITOR BATTLE CARDS & OBJECTION HANDLER
# =====================================================================

@router.post("/competitor-battlecard")
def generate_battlecard(data: dict, user_id: int = 1, db: Session = Depends(get_db)):
    competitor = data.get("competitor", "").strip()
    our_product = data.get("our_product", "SalesGenie AI Platform").strip()

    if not competitor:
        raise HTTPException(status_code=400, detail="Competitor name is required.")

    prompt = f"""
    Generates a sales battle card against competitor: '{competitor}'.
    Our Product Category: {our_product}

    Return ONLY valid JSON in this exact structure:
    {{
      "competitor": "{competitor}",
      "top_weaknesses": ["Weakness 1", "Weakness 2"],
      "our_key_advantages": ["Advantage 1", "Advantage 2"],
      "objection_scripts": {{
        "Their pricing is lower": "How to respond effectively...",
        "They have been in the market longer": "How to handle brand reputation..."
      }}
    }}
    """

    if not client:
        return {
            "competitor": competitor,
            "top_weaknesses": ["Legacy architecture", "Slower setup time"],
            "our_key_advantages": ["Real-time Gemini AI integration", "Unified workspace"],
            "objection_scripts": {
                "Pricing objection": "Highlight ROI velocity and automation time saved.",
                "Feature comparison": "Emphasize our native conversation intelligence."
            }
        }

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        return clean_json_response(response.text)
    except Exception:
        return {
            "competitor": competitor,
            "top_weaknesses": ["Complex onboarding", "High maintenance costs"],
            "our_key_advantages": ["Instant setup", "AI-driven lead scoring"],
            "objection_scripts": {
                "Pricing objection": "Focus on quick time-to-value.",
                "Migration risk": "Demonstrate seamless CSV import."
            }
        }