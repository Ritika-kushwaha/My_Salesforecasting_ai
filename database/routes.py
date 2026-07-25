
from unittest import result

from sqlalchemy import text
from database.ai import model
from sqlalchemy.orm import Session

<<<<<<< Updated upstream
from database.database import get_db
from database.models import Lead
from sqlalchemy import func
import json
from fastapi import APIRouter, Depends, HTTPException
from database.models import User
from database.schemas import UserCreate
from database.schemas import UserLogin

=======
from database.ai import client
from database.database import get_db
from database.models import Campaign, Company, Lead, SalesInteraction, User
from database.schemas import LeadCreate, UserCreate, UserLogin
from typing import List
>>>>>>> Stashed changes
router = APIRouter()


@router.get("/")
def home():
    return {"message": "SalesGenie API Running"}


# --- DASHBOARD ENDPOINT (GLOBAL OR PER USER) ---
@router.get("/dashboard")
<<<<<<< Updated upstream
def dashboard(db: Session = Depends(get_db)):

    total_leads = db.query(Lead).count()

    industries = (
        db.query(
            Lead.industry,
            func.count(Lead.id)
        )
        .group_by(Lead.industry)
        .all()
    )

    recent = (
        db.query(Lead)
        .order_by(Lead.id.desc())
        .limit(5)
        .all()
    )

    return {
        "total_leads": total_leads,
        "industries": [
            {
                "industry": i,
                "count": c
            }
            for i, c in industries
        ],
        "recent_leads": [
            {
                "name": l.name,
                "company": l.company,
                "industry": l.industry
            }
            for l in recent
        ]
    }

=======
def dashboard(user_id: int = None, db: Session = Depends(get_db)):
    # Returns global stats across all users if no filter is required
    query_leads = db.query(Lead)
    if user_id:
        query_leads = query_leads.filter(Lead.user_id == user_id)

    total_leads = query_leads.count()
    total_companies = query_leads.distinct(Lead.company).count()
    qualified_leads = query_leads.filter(Lead.status == "Qualified").count()

    avg_score_res = db.query(func.avg(Lead.lead_score)).scalar()
    average_score = float(avg_score_res) if avg_score_res else 0.0

    return {
        "total_leads": total_leads,
        "qualified_leads": qualified_leads,
        "companies": total_companies,
        "average_score": average_score,
    }


# --- USER AUTHENTICATION ---
@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Email is already registered."
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password,  # In production, use password hashing
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {
            "message": "User created successfully",
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email,
            },
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error.")


>>>>>>> Stashed changes
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()
<<<<<<< Updated upstream

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid password")
=======
    if not db_user or db_user.password != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
>>>>>>> Stashed changes

    return {
        "message": "Login successful",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email
        }
    }


<<<<<<< Updated upstream
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.email == user.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password      # We'll hash later
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Signup successful"}


@router.post("/add-lead")
def add_lead(data: dict, db: Session = Depends(get_db)):

    lead = Lead(
        name=data["name"],
        email=data["email"],
        phone=data["phone"],
        company=data["company"],
        industry=data["industry"]
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    return {
        "success": True,
        "message": "Lead Added Successfully",
        "lead_id": lead.id
    }

@router.get("/leads")
def get_leads(db: Session = Depends(get_db)):

    leads = db.query(Lead).all()

=======
# --- LEADS ENDPOINTS ---
@router.get("/leads")
def get_leads(user_id: int = None, db: Session = Depends(get_db)):
    # Returns ALL leads stored in PostgreSQL across all accounts
    query = db.query(Lead)
    if user_id:
        # Optional: query = query.filter(Lead.user_id == user_id)
        pass
    leads = query.all()

>>>>>>> Stashed changes
    return [
        {
            "id": l.id,
            "name": l.name,
<<<<<<< Updated upstream
            "email": l.email,
            "phone": l.phone,
            "company": l.company,
            "industry": l.industry,
            "status": l.status,
            "created_at": l.created_at
=======
            "contact_name": l.name,
            "company": l.company,
            "company_name": l.company,
            "email": l.email,
            "phone": l.phone,
            "industry": l.industry,
            "company_size": l.company_size,
            "revenue": l.revenue,
            "lead_score": l.lead_score,
            "priority": l.priority,
            "status": l.status,
            "lead_status": l.status,
>>>>>>> Stashed changes
        }
        for l in leads
    ]

<<<<<<< Updated upstream
@router.post("/analyze-company")
def analyze_company(data: dict):

    prompt = f"""
Analyze the following company.

Company: {data.get("company")}
Website: {data.get("website")}
Industry: {data.get("industry")}

Return ONLY valid JSON.
Do not include markdown, explanations, or extra text.
=======

@router.post("/leads")
def create_lead(
    lead: LeadCreate, user_id: int = 1, db: Session = Depends(get_db)
):
    db_lead = Lead(
        user_id=user_id,
        name=lead.name,
        company=lead.company,
        email=lead.email,
        phone=lead.phone,
        industry=lead.industry,
        company_size=lead.company_size,
        revenue=lead.revenue,
        priority=lead.priority,
        status=lead.status,
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


# --- COMPANIES ENDPOINTS ---
@router.get("/companies")
def get_companies(db: Session = Depends(get_db)):
    # Returns ALL companies in database
    return db.query(Company).all()


@router.post("/analyze-company")
def analyze_company(data: dict, user_id: int = 1, db: Session = Depends(get_db)):
    company_name = data.get("company", "").strip()
    website = data.get("website", "").strip()
    industry = data.get("industry", "").strip()

    # 1. Reject empty or invalid input immediately
    if not company_name or len(company_name) < 2:
        raise HTTPException(
            status_code=400, 
            detail="Please provide a valid Company Name (at least 2 characters)."
        )

    # 2. Add fallback defaults for optional fields
    website_str = website if website else "Not Provided"
    industry_str = industry if industry else "General Business / Technology"

    prompt = f"""
You are an expert sales intelligence analyst. Analyze this company for B2B sales potential:

Company Name: {company_name}
Website: {website_str}
Industry: {industry_str}
>>>>>>> Stashed changes

{{
<<<<<<< Updated upstream
  "company": "",
  "industry": "",
  "lead_score": 0,
  "grade": "",
  "company_summary": "",
  "sales_opportunity": "",
  "recommended_sales_approach": ""
}}
"""


    response = model.generate_content(prompt)

    text = response.text.strip()

    # remove markdown if Gemini returns ```json
    text = text.replace("```json", "").replace("```", "").strip()
    print(text)
    try:
        result = json.loads(text)
    except Exception:
        return {
            "company": data.get("company"),
            "industry": data.get("industry", "Unknown"),
            "lead_score": 0,
            "grade": "N/A",
            "company_summary": text,
            "sales_opportunity": "Not Available",
            "recommended_sales_approach": "Not Available"
        }
    return result

=======
  "company": "{company_name}",
  "industry": "{industry_str}",
  "lead_score": 85,
  "grade": "A",
  "company_summary": "Comprehensive overview of {company_name}...",
  "sales_opportunity": "Key pain points and expansion opportunities...",
  "recommended_sales_approach": "Actionable outreach strategy..."
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        result = clean_json_response(response.text)
    except Exception as e:
        # Structured fallback if Gemini API fails
        result = {
            "company": company_name,
            "industry": industry_str,
            "lead_score": 65,
            "grade": "B",
            "company_summary": f"Initial research profile created for {company_name}.",
            "sales_opportunity": "Standard discovery call recommended to evaluate current needs.",
            "recommended_sales_approach": "Send an introductory email focusing on value propositions.",
        }

    # Save or update Company in database
    existing = db.query(Company).filter(Company.company_name == company_name).first()
    if not existing:
        new_company = Company(
            user_id=user_id,
            company_name=company_name,
            website=website_str,
            industry=industry_str,
            description=result.get("company_summary", ""),
        )
        db.add(new_company)
        db.commit()

    return result

# Add this endpoint in database/routes.py
@router.post("/leads/bulk")
def create_leads_bulk(leads: List[dict], user_id: int = 1, db: Session = Depends(get_db)):
    try:
        created_count = 0
        skipped_count = 0
        
        # Fetch existing lead emails for this user to check against
        existing_emails = {
            lead[0].lower() 
            for lead in db.query(Lead.email).filter(Lead.user_id == user_id).all() 
            if lead[0]
        }

        for lead in leads:
            def clean_str(val, default=""):
                if val is None or (isinstance(val, float) and math.isnan(val)):
                    return default
                return str(val).strip()

            company_val = clean_str(lead.get("company") or lead.get("company_name"), "Unknown Company")
            name_val = clean_str(lead.get("name") or lead.get("contact_name"), "Unknown Contact")
            email_val = clean_str(lead.get("email"), f"contact@{company_val.lower().replace(' ', '')}.com").lower()

            # SKIP IF EMAIL ALREADY EXISTS IN DATABASE
            if email_val in existing_emails:
                skipped_count += 1
                continue

            raw_revenue = lead.get("revenue")
            revenue_val = 0.0
            if raw_revenue is not None and not (isinstance(raw_revenue, float) and math.isnan(raw_revenue)):
                try:
                    rev_str = str(raw_revenue).replace("$", "").replace(",", "").replace("M", "").replace("+", "").strip()
                    revenue_val = float(rev_str)
                except ValueError:
                    revenue_val = 0.0

            db_lead = Lead(
                user_id=user_id,
                name=name_val,
                company=company_val,
                email=email_val,
                phone=clean_str(lead.get("phone"), "N/A"),
                industry=clean_str(lead.get("industry"), "General"),
                company_size=clean_str(lead.get("company_size"), "1-10"),
                revenue=revenue_val,
                priority=clean_str(lead.get("priority"), "Medium"),
                status=clean_str(lead.get("status"), "New"),
            )
            db.add(db_lead)
            existing_emails.add(email_val)  # Track added email in loop
            created_count += 1

        db.commit()
        return {
            "message": f"Imported {created_count} new leads! ({skipped_count} duplicate emails skipped)"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    
    
    
# --- AI EMAIL GENERATION & CAMPAIGNS ---
@router.post("/generate-email")
def generate_email(
    data: dict, user_id: int = 1, db: Session = Depends(get_db)
):
    company = data.get("company", "")
    name = data.get("name", "")
    industry = data.get("industry", "")
    product = data.get("product", "Our Product")

    prompt = f"""
Generate a high-converting professional cold sales email.

Recipient: {name}
Company: {company}
Industry: {industry}
Product/Value Proposition: {product}

Return ONLY the email body text.
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        email_text = response.text.strip()

        # Save Campaign to Database
        new_campaign = Campaign(
            user_id=user_id,
            title=f"Outreach to {company} ({name})",
            subject=f"Connecting with {company}",
            body=email_text,
            target_industry=industry,
            status="Draft",
        )
        db.add(new_campaign)
        db.commit()
        db.refresh(new_campaign)

        return {"email": email_text, "campaign_id": new_campaign.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

>>>>>>> Stashed changes

@router.get("/campaigns")
def get_campaigns(db: Session = Depends(get_db)):
    # Returns ALL campaigns across the team
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    return [
        {
            "id": c.id,
            "title": c.title,
            "subject": c.subject,
            "body": c.body,
            "target_industry": c.target_industry,
            "status": c.status,
            "created_at": (
                c.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if c.created_at
                else None
            ),
        }
        for c in campaigns
    ]


@router.delete("/campaigns/{campaign_id}")
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=404, detail="Campaign record not found."
        )

    db.delete(campaign)
    db.commit()
    return {"success": True, "message": "Campaign deleted successfully."}


# --- LEAD SCORING ---
@router.post("/lead-score")
<<<<<<< Updated upstream
def lead_score(data: dict):
=======
def lead_score(
    data: dict, user_id: int = 1, db: Session = Depends(get_db)
):
    company = data.get("company", "").strip()
    industry = data.get("industry", "").strip()
    company_size = data.get("company_size", "").strip()
    revenue = data.get("revenue", "").strip()
    budget = data.get("budget", "").strip()
    decision_maker = data.get("decision_maker", "No")
>>>>>>> Stashed changes

    prompt = f"""
You are an expert B2B sales analyst.

Evaluate this lead.

Company: {data["company"]}
Industry: {data["industry"]}
Company Size: {data["company_size"]}
Annual Revenue: {data["revenue"]}
Budget: {data["budget"]}
Decision Maker: {data["decision_maker"]}

Return ONLY valid JSON.

{{
<<<<<<< Updated upstream
  "lead_score":91,
  "grade":"A",
  "priority":"High",
  "conversion_probability":"84%",
  "qualification":"Hot Lead",
  "company_summary":"Google is a global technology leader specializing in cloud computing, AI, and digital advertising.",
  "sales_opportunity":"Excellent opportunity for enterprise AI solutions.",
  "recommended_sales_approach":"Schedule a technical demo followed by executive outreach.",
  "reasons":[
      "Large enterprise",
      "Budget available",
      "Technology industry",
      "Decision maker identified"
  ],
  "next_action":"Contact within 24 hours."
=======
  "lead_score": 88,
  "grade": "A",
  "priority": "High",
  "conversion_probability": "80%",
  "qualification": "Qualified Lead",
  "company_summary": "High potential prospect...",
  "sales_opportunity": "Enterprise solution opportunities...",
  "recommended_sales_approach": "Contact decision maker directly.",
  "reasons": ["High revenue potential", "Budget allocated"],
  "next_action": "Schedule product demo within 24 hours."
>>>>>>> Stashed changes
}}
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    # Remove markdown if Gemini wraps the response
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(text)
        return result

    except Exception:
<<<<<<< Updated upstream
        return {
            "lead_score": 0,
            "grade": "N/A",
            "priority": "Unknown",
            "conversion_probability": "0%",
            "qualification": "Unknown",
            "company_summary": text,
            "sales_opportunity": "Not Available",
            "recommended_sales_approach": "Not Available",
            "reasons": [],
            "next_action": "Try again."
        }


@router.post("/generate-email")
def generate_email(data: dict):

    prompt = f"""
Generate a professional cold sales email.

Contact Name: {data.get("name")}
Company: {data.get("company")}
Industry: {data.get("industry")}
Product: {data.get("product")}

Return only the email body.
"""

    response = model.generate_content(prompt)

    return {
        "email": response.text.strip()
    }
=======
        result = {
            "lead_score": 50,
            "grade": "C",
            "priority": "Medium",
            "conversion_probability": "50%",
            "qualification": "Warm Lead",
            "company_summary": "Standard lead evaluation.",
            "sales_opportunity": "Standard opportunity.",
            "recommended_sales_approach": "Send intro email.",
            "reasons": ["Standard metrics"],
            "next_action": "Follow up in 48 hours.",
        }

    # Update Lead in Database if present
    existing_lead = db.query(Lead).filter(Lead.company == company).first()
    if existing_lead:
        existing_lead.lead_score = result.get("lead_score", 50)
        existing_lead.priority = result.get("priority", "Medium")
        existing_lead.status = result.get("qualification", "Qualified")
        db.commit()

    return result


# --- CONVERSATIONS & CRM ACTIVITIES ---
@router.get("/conversations")
def get_conversations(lead_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(SalesInteraction)
        .filter(SalesInteraction.lead_id == lead_id)
        .order_by(SalesInteraction.timestamp.asc())
        .all()
    )
    return [
        {
            "id": m.id,
            "sender": m.sender,
            "message": m.message,
            "timestamp": (
                m.timestamp.strftime("%b %d, %H:%M") if m.timestamp else ""
            ),
        }
        for m in messages
    ]


@router.post("/conversations")
def send_message(
    data: dict, user_id: int = 1, db: Session = Depends(get_db)
):
    lead_id = data.get("lead_id")
    user_message = data.get("message", "").strip()
    generate_ai_reply = data.get("generate_ai_reply", False)

    if not lead_id or not user_message:
        raise HTTPException(
            status_code=400, detail="lead_id and message are required."
        )

    # Save User/Sales Rep message
    user_msg_entry = SalesInteraction(
        user_id=user_id,
        lead_id=lead_id,
        sender="User",
        message=user_message,
    )
    db.add(user_msg_entry)
    db.commit()

    ai_reply_text = None
    if generate_ai_reply:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        company_name = lead.company if lead else "the client"

        prompt = f"""
You are an expert sales copilot for SalesGenie AI.
Talking to prospect from '{company_name}'.
User noted: "{user_message}"
Provide a clear, persuasive sales response.
"""
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            ai_reply_text = response.text.strip()

            ai_msg_entry = SalesInteraction(
                user_id=user_id,
                lead_id=lead_id,
                sender="AI Assistant",
                message=ai_reply_text,
            )
            db.add(ai_msg_entry)
            db.commit()
        except Exception:
            ai_reply_text = "Unable to generate reply at this moment."

    return {"success": True, "ai_reply": ai_reply_text}
>>>>>>> Stashed changes
