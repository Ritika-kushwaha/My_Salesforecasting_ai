import json
import logging
import math
import os
import re
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from google import genai
from pydantic import BaseModel
import requests
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import Company, Conversation, Lead, User

logger = logging.getLogger(__name__)

router = APIRouter()

# -------------------------------------------------------------------
# ENVIRONMENT & CONFIGURATION
# -------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8501/").strip()

REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8501/").strip()


def sanitize_status(val: any) -> str:
    """Ensures status is always a valid CRM stage string and never an integer or index."""
    if val is None:
        return "New"
    val_str = str(val).strip()
    if val_str in ["", "1", "0", "None", "null", "true", "false"]:
        return "New"

    mapping = {
        "new": "New",
        "contacted": "Contacted",
        "qualified": "Qualified",
        "proposal sent": "Proposal Sent",
        "proposal": "Proposal Sent",
        "closed won": "Closed Won",
        "won": "Closed Won",
        "closed lost": "Closed Lost",
        "lost": "Closed Lost"
    }
    return mapping.get(val_str.lower(), val_str[:50])


def clean_json_response(text_data: str) -> dict:
    """Utility to clean Markdown code block formatting from Gemini responses."""
    cleaned = re.sub(r"```json\s*", "", text_data)
    cleaned = re.sub(r"```\s*$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return {}


# ==========================================
# 1. USER AUTHENTICATION & GOOGLE OAUTH
# ==========================================
class GoogleAuthRequest(BaseModel):
    token: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None


@router.post("/auth/sync-user")
def sync_user(data: dict, db: Session = Depends(get_db)):
    email = data.get("email", "").strip().lower()
    name = data.get("name", "Sales Rep").strip()
    avatar = data.get("avatar", "")

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, name=name, password="oauth_synced_account")
        db.add(user)
        db.commit()
        db.refresh(user)

    return {"id": user.id, "email": user.email, "name": user.name, "avatar": getattr(user, "avatar", avatar)}


@router.post("/auth/google")
def google_auth(data: GoogleAuthRequest, db: Session = Depends(get_db)):
    user_email = None
    user_name = None

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

            if access_token:
                user_info_res = requests.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10,
                )
                user_info = user_info_res.json()
                user_email = user_info.get("email")
                user_name = user_info.get("name")
        except Exception as e:
            logger.error(f"Google token exchange failed: {e}")

    if not user_email and data.email:
        user_email = data.email
        user_name = data.name

    if not user_email:
        user_email = "google.user@salesgenie.ai"
        user_name = "Google User"

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        user = User(email=user_email, name=user_name or "Google User", password="oauth_google_account")
        db.add(user)
        db.commit()
        db.refresh(user)

    return {
        "status": "success",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
        },
    }


@router.get("/auth/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    try:
        token_res = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
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
            raise HTTPException(status_code=400, detail="Invalid authorization code from Google.")

        user_info_res = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        google_user = user_info_res.json()
        email = google_user.get("email")
        name = google_user.get("name", "Google User")
        avatar = google_user.get("picture", "")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, name=name, password="oauth_google_account")
            db.add(user)
            db.commit()
            db.refresh(user)

        return {
            "message": "Google authentication successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "avatar": avatar,
            },
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user_name = email.split("@")[0].title() if email else "Sales Rep"
        user = User(email=email, name=user_name, password=password if password else "password123")
        db.add(user)
        db.commit()
        db.refresh(user)

    return {
        "status": "success",
        "message": "Login successful",
        "user": {"id": user.id, "name": user.name, "email": user.email},
    }


@router.post("/signup")
def signup(data: dict, db: Session = Depends(get_db)):
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    name = data.get("name", "").strip()

    if not email or not password or not name:
        raise HTTPException(status_code=400, detail="Name, Email, and Password are required.")

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return {
            "status": "success",
            "message": "User exists",
            "user": {"id": existing_user.id, "name": existing_user.name, "email": existing_user.email},
        }

    new_user = User(name=name, email=email, password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "status": "success",
        "message": "User created successfully",
        "user": {"id": new_user.id, "name": new_user.name, "email": new_user.email},
    }


# =====================================================================
# 2. LEAD MANAGEMENT ENDPOINTS (SELF-HEALING & SANITIZED)
# =====================================================================
# =====================================================================
# 2. LEAD MANAGEMENT ENDPOINTS (ORDERED CHRONOLOGICALLY / AT LAST)
# =====================================================================
@router.get("/leads")
def get_leads(user_id: int = Query(1), db: Session = Depends(get_db)):
    # .order_by(Lead.id.asc()) appends newest leads at the bottom/last
    leads = db.query(Lead).filter(Lead.user_id == user_id).order_by(Lead.id.asc()).all()
    result = []
    dirty = False

    for lead in leads:
        raw_status = getattr(lead, "status", None) or getattr(lead, "lead_status", "New")
        clean_status = sanitize_status(raw_status)

        # Auto-heal any legacy records stored with status '1' or empty
        if str(raw_status).strip() in ["", "1", "0", "None", "null"]:
            lead.status = "New"
            dirty = True

        result.append(
            {
                "id": lead.id,
                "name": getattr(lead, "name", None) or getattr(lead, "contact_name", "N/A"),
                "company": getattr(lead, "company", None) or getattr(lead, "company_name", "N/A"),
                "email": lead.email,
                "phone": lead.phone or "N/A",
                "industry": lead.industry or "General",
                "company_size": lead.company_size or "1-10",
                "revenue": str(lead.revenue or "0"),
                "priority": lead.priority or "Medium",
                "status": clean_status,
                "created_at": lead.created_at.isoformat() if lead.created_at else None,
            }
        )

    if dirty:
        try:
            db.commit()
        except Exception:
            db.rollback()

    return result


@router.post("/leads")
def create_lead(data: dict, user_id: int = Query(1), db: Session = Depends(get_db)):
    name = data.get("name") or data.get("contact_name")
    company = data.get("company") or data.get("company_name")
    email = data.get("email")

    if not name or not company or not email:
        raise HTTPException(status_code=400, detail="Name, Company, and Email are required.")

    status_val = sanitize_status(data.get("status"))

    new_lead = Lead(
        user_id=user_id,
        name=name,
        company=company,
        email=email,
        phone=data.get("phone", ""),
        industry=data.get("industry", "General"),
        company_size=data.get("company_size", "1-10"),
        revenue=str(data.get("revenue", "0")),
        priority=data.get("priority", "Medium"),
        status=status_val,
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return {"message": "Lead created successfully", "lead_id": new_lead.id}


@router.put("/leads/{lead_id}")
def update_lead(lead_id: int, data: dict, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead #{lead_id} not found.")

    try:
        # Include all fields: name, company, email, phone, industry, company_size, revenue, priority
        editable_fields = [
            "name",
            "company",
            "email",
            "phone",
            "industry",
            "company_size",
            "revenue",
            "priority",
        ]
        for field in editable_fields:
            if field in data and data[field] is not None:
                setattr(lead, field, str(data[field]))

        if "status" in data and data["status"] is not None:
            lead.status = sanitize_status(data["status"])

        db.commit()
        db.refresh(lead)
        return {"message": f"Lead {lead_id} updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update lead: {str(e)}")

@router.delete("/leads/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead #{lead_id} not found.")

    try:
        db.query(Conversation).filter(Conversation.lead_id == lead_id).delete()
        db.delete(lead)
        db.commit()
        return {"message": f"Lead #{lead_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/leads/bulk")
def create_leads_bulk(leads: List[dict], user_id: int = Query(1), db: Session = Depends(get_db)):
    try:
        created_count = 0
        for lead in leads:
            company_val = str(lead.get("company") or lead.get("company_name") or "Unknown Company").strip()
            name_val = str(lead.get("name") or lead.get("contact_name") or "Unknown Contact").strip()
            email_val = str(lead.get("email") or f"contact@{company_val.lower().replace(' ', '')}.com").strip().lower()

            db_lead = Lead(
                user_id=user_id,
                name=name_val,
                company=company_val,
                email=email_val,
                phone=str(lead.get("phone") or "N/A"),
                industry=str(lead.get("industry") or "General"),
                company_size=str(lead.get("company_size") or "1-10"),
                revenue=str(lead.get("revenue") or "0"),
                priority=str(lead.get("priority") or "Medium"),
                status=sanitize_status(lead.get("status")),
            )
            db.add(db_lead)
            created_count += 1

        db.commit()
        return {"message": f"Successfully imported {created_count} leads!", "count": created_count}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database import error: {str(e)}")


# =====================================================================
# 3. AI OUTREACH GENERATOR
# =====================================================================
@router.post("/generate-outreach")
def generate_outreach(data: dict, user_id: int = Query(1)):
    name = data.get("name", "Prospect").strip()
    company = data.get("company", "Target Company").strip()
    industry = data.get("industry", "General Industry").strip()
    channel = data.get("channel", "Cold Email").strip()
    tone = data.get("tone", "Professional & Persuasive").strip()
    value_prop = data.get("value_prop", "").strip()

    prompt = f"""
Write a high-converting {channel} for a prospective buyer.
- Contact Name: {name}
- Target Company: {company}
- Industry: {industry}
- Tone: {tone}
- Value Proposition: {value_prop if value_prop else 'AI-driven automation that reduces sales cycle times'}

Return ONLY valid JSON in this exact structure:
{{
  "subject": "Compelling subject line",
  "body": "Personalized message body tailored to the prospect..."
}}
"""
    if not client:
        return {
            "subject": f"Quick question regarding {company}'s growth",
            "body": f"Hi {name},\n\nI noticed {company}'s work in {industry}. We help sales teams scale messaging without sacrificing personalization.\n\nWould you be open to a brief chat this week?\n\nBest regards,\nSalesGenie Team",
        }

    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return clean_json_response(response.text)
    except Exception:
        return {
            "subject": f"Exploring growth opportunities for {company}",
            "body": f"Hi {name},\n\nHope this finds you well. Given your focus in {industry}, I wanted to reach out regarding how {company} can benefit from sales automation.\n\nBest regards,\nSalesGenie Team",
        }


# =====================================================================
# 4. CONVERSATION INTELLIGENCE
# =====================================================================
@router.get("/conversations")
def get_conversations(lead_id: int, user_id: int = Query(1), db: Session = Depends(get_db)):
    conversations = (
        db.query(Conversation)
        .filter(Conversation.lead_id == lead_id, Conversation.user_id == user_id)
        .order_by(Conversation.id.asc())
        .all()
    )
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
def analyze_conversation(data: dict, user_id: int = Query(1), db: Session = Depends(get_db)):
    lead_id = data.get("lead_id")
    transcript = data.get("transcript", "").strip()
    interaction_type = data.get("interaction_type", "Discovery Call")

    if not lead_id or not transcript:
        raise HTTPException(status_code=400, detail="lead_id and transcript are required.")

    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == user_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    ai_data = None
    if client:
        prompt = f"""
Analyze this sales meeting transcript ({interaction_type}):
\"\"\"{transcript}\"\"\"

Return ONLY valid JSON in this exact structure:
{{
  "summary": "Concise 2-3 sentence executive discussion summary...",
  "key_points": ["Key requirement 1", "Key point 2"],
  "action_items": ["Action item 1", "Action item 2"],
  "recommended_stage": "Qualified"
}}
"""
        try:
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            ai_data = clean_json_response(response.text)
        except Exception:
            ai_data = None

    if not ai_data or "summary" not in ai_data:
        ai_data = {
            "summary": f"Meeting notes recorded for {interaction_type}. Prospect discussed operational requirements and next evaluation steps.",
            "key_points": ["Customer requirements reviewed", "Timeline and technical next steps evaluated"],
            "action_items": ["Send follow-up email and proposal", "Schedule technical demo"],
            "recommended_stage": "Qualified",
        }

    raw_stage = str(ai_data.get("recommended_stage", "")).strip()
    lead.status = sanitize_status(raw_stage)

    try:
        new_conv = Conversation(
            user_id=user_id,
            lead_id=lead_id,
            interaction_type=interaction_type,
            transcript=transcript,
            summary=ai_data.get("summary", ""),
            sender="AI",
            message=ai_data.get("summary", ""),
        )
        db.add(new_conv)
        db.commit()
        db.refresh(new_conv)
        return {"message": "Conversation analyzed and saved successfully", "data": ai_data}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# =====================================================================
# 5. COMPANY INTELLIGENCE
# =====================================================================
@router.post("/analyze-company")
def analyze_company(data: dict, user_id: int = Query(1), db: Session = Depends(get_db)):
    company_name = data.get("company", "").strip()
    website = data.get("website", "").strip()
    industry = data.get("industry", "Technology & SaaS").strip()

    if not company_name:
        raise HTTPException(status_code=400, detail="Company name is required.")

    ai_data = None
    if client:
        prompt = f"""
Analyze this company for B2B sales potential:
Company Name: {company_name}
Website: {website}
Industry: {industry}

Return ONLY valid JSON in this exact structure:
{{
  "lead_score": 85,
  "grade": "A",
  "industry": "{industry}",
  "company_summary": "Comprehensive overview of {company_name}...",
  "sales_opportunity": "Key pain points and expansion opportunities...",
  "recommended_sales_approach": "Actionable outreach strategy..."
}}
"""
        try:
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            ai_data = clean_json_response(response.text)
        except Exception:
            ai_data = None

    if not ai_data or "company_summary" not in ai_data:
        ai_data = {
            "lead_score": 80,
            "grade": "A-",
            "industry": industry,
            "company_summary": f"{company_name} is an active enterprise in the {industry} market.",
            "sales_opportunity": "Streamlining manual sales processes and accelerating pipeline velocity.",
            "recommended_sales_approach": "Lead with a customized demo focused on efficiency gains and automated workflows.",
        }

    try:
        new_comp = Company(
            user_id=user_id,
            company_name=company_name,
            website=website,
            industry=industry,
            description=ai_data.get("company_summary", ""),
        )
        db.add(new_comp)
        db.commit()
    except Exception:
        db.rollback()

    return ai_data


# =====================================================================
# 6. DASHBOARD METRICS
# =====================================================================
@router.get("/dashboard")
def get_dashboard_data(user_id: int = Query(1), db: Session = Depends(get_db)):
    query_leads = db.query(Lead).filter(Lead.user_id == user_id)
    total_leads = query_leads.count()
    high_priority_count = query_leads.filter(func.lower(Lead.priority) == "high").count()

    qualified_count = 0
    try:
        qualified_count = query_leads.filter(
            func.lower(Lead.status).ilike("%qualif%")
            | func.lower(Lead.status).ilike("%proposal%")
            | func.lower(Lead.status).ilike("%closed won%")
        ).count()
    except Exception:
        qualified_count = 0

    conversion_rate = round((qualified_count / total_leads * 100), 1) if total_leads > 0 else 0.0

    total_companies = 0
    try:
        total_companies = db.query(Company).filter(Company.user_id == user_id).count()
    except Exception:
        pass

    return {
        "total_leads": total_leads,
        "high_priority_leads": high_priority_count,
        "qualified_leads": qualified_count,
        "conversion_rate": conversion_rate,
        "total_companies": total_companies,
    }