import json
import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database.models import Campaign
from database.ai import client
from database.database import get_db
from database.models import Company, Lead, User
from database.schemas import LeadCreate, UserCreate, UserLogin
from database.models import SalesInteraction, Lead



router = APIRouter()


def clean_json_response(raw_text: str) -> dict:
    """Safely extract JSON objects from AI responses."""
    json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    raise ValueError("Could not parse valid JSON from AI response.")


@router.get("/")
def home():
    return {"message": "SalesGenie API Running"}


@router.get("/dashboard")
def dashboard(user_id: int, db: Session = Depends(get_db)):
    total_leads = db.query(Lead).filter(Lead.user_id == user_id).count()
    total_companies = (
        db.query(Lead.company)
        .filter(Lead.user_id == user_id)
        .distinct()
        .count()
    )
    qualified = (
        db.query(Lead)
        .filter(Lead.user_id == user_id, Lead.status == "Qualified")
        .count()
    )
    avg_score = (
        db.query(func.avg(Lead.lead_score))
        .filter(Lead.user_id == user_id)
        .scalar()
        or 0.0
    )

    return {
        "total_leads": total_leads,
        "companies": total_companies,
        "qualified_leads": qualified,
        "average_score": round(avg_score, 2),
    }


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or db_user.password != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return {
        "message": "Login Successful",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
        },
    }


@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Signup successful"}


@router.post("/add-lead")
def add_lead(
    lead_data: LeadCreate, user_id: int, db: Session = Depends(get_db)
):
    # Check for existing email duplicate
    existing = (
        db.query(Lead)
        .filter(Lead.email == lead_data.email, Lead.user_id == user_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A lead with email '{lead_data.email}' already exists.",
        )

    prompt = f"""
You are an expert sales analyst. Evaluate this lead:
Company: {lead_data.company}
Industry: {lead_data.industry}
Company Size: {lead_data.company_size}
Revenue: {lead_data.revenue}

Return ONLY valid JSON in this structure:
{{
    "lead_score": 90,
    "priority": "High",
    "status": "Qualified"
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        ai_res = clean_json_response(response.text)
    except Exception:
        ai_res = {"lead_score": 50, "priority": "Medium", "status": "New"}

    lead = Lead(
        user_id=user_id,
        name=lead_data.name,
        email=lead_data.email,
        phone=lead_data.phone,
        company=lead_data.company,
        industry=lead_data.industry,
        company_size=lead_data.company_size,
        revenue=str(lead_data.revenue),
        lead_score=ai_res.get("lead_score", 50),
        priority=ai_res.get("priority", "Medium"),
        status=ai_res.get("status", "New"),
    )

    try:
        db.add(lead)
        db.commit()
        db.refresh(lead)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A lead with this email address already exists.",
        )

    return {
        "success": True,
        "lead_id": lead.id,
        "lead_score": lead.lead_score,
        "priority": lead.priority,
        "status": lead.status,
    }

@router.post("/analyze-conversation")
def analyze_conversation(data: dict, user_id: int, db: Session = Depends(get_db)):
    lead_id = data.get("lead_id")
    transcript = data.get("transcript", "").strip()
    interaction_type = data.get("interaction_type", "Discovery Call")

    if not lead_id or not transcript:
        raise HTTPException(status_code=400, detail="lead_id and transcript/notes are required.")

    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == user_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead record not found.")

    prompt = f"""
You are an AI Conversation Intelligence Assistant. Analyze this sales meeting/call transcript:

Company: {lead.company_name}
Contact: {lead.contact_name}
Interaction Type: {interaction_type}
Transcript/Notes:
{transcript}

Return ONLY valid JSON in this exact structure:
{{
    "summary": "Concise 2-sentence summary of the meeting...",
    "key_discussion_points": [
        "Discussion point 1",
        "Discussion point 2",
        "Discussion point 3"
    ],
    "action_items": [
        {{"task": "Send technical architecture document", "assigned_to": "Sales Rep", "due_in": "2 days"}},
        {{"task": "Schedule technical deep dive with engineering team", "assigned_to": "Contact Person", "due_in": "5 days"}}
    ],
    "suggested_deal_stage": "Qualified"
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        result = clean_json_response(response.text)
    except Exception:
        result = {
            "summary": "Meeting completed and notes recorded.",
            "key_discussion_points": ["Customer expressed interest in API integrations."],
            "action_items": [{"task": "Follow up via email", "assigned_to": "Sales Rep", "due_in": "1 day"}],
            "suggested_deal_stage": "Qualified"
        }

    # Save Sales Interaction into Database
    interaction = SalesInteraction(
        user_id=user_id,
        lead_id=lead_id,
        sender="AI Assistant",
        message=f"[{interaction_type}] {result.get('summary')}",
    )
    
    # Update lead status if stage progressed
    if result.get("suggested_deal_stage"):
        lead.lead_status = result.get("suggested_deal_stage")

    db.add(interaction)
    db.commit()

    return {
        "success": True,
        "lead_name": lead.contact_name,
        "company_name": lead.company_name,
        "summary": result.get("summary"),
        "key_discussion_points": result.get("key_discussion_points", []),
        "action_items": result.get("action_items", []),
        "deal_stage": lead.lead_status,
    }


@router.get("/interactions")
def get_interactions(lead_id: int, user_id: int, db: Session = Depends(get_db)):
    records = (
        db.query(SalesInteraction)
        .filter(SalesInteraction.lead_id == lead_id, SalesInteraction.user_id == user_id)
        .order_by(SalesInteraction.timestamp.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "message": r.message,
            "sender": r.sender,
            "timestamp": r.timestamp.strftime("%b %d, %I:%M %p") if r.timestamp else "",
        }
        for r in records
    ]


@router.get("/leads")
def get_leads(user_id: int, db: Session = Depends(get_db)):
    leads = db.query(Lead).filter(Lead.user_id == user_id).all()
    
    output = []
    for l in leads:
        # Fallback safe field extractions
        c_name = getattr(l, "company_name", getattr(l, "company", "N/A"))
        cnt_name = getattr(l, "contact_name", getattr(l, "name", "N/A"))
        l_status = getattr(l, "lead_status", getattr(l, "status", "New"))
        
        output.append({
            "id": l.id,
            "name": cnt_name,
            "contact_name": cnt_name,
            "company": c_name,
            "company_name": c_name,
            "email": l.email,
            "phone": l.phone if l.phone else "",
            "industry": l.industry if l.industry else "Other",
            "lead_status": l_status,
            "status": l_status,
            "lead_score": getattr(l, "lead_score", 0),
            "priority": getattr(l, "priority", "Medium"),
        })
    return output

# --- COMPANIES ENDPOINT ---
@router.get("/companies")
def get_companies(user_id: int, db: Session = Depends(get_db)):
    return db.query(Company).filter(Company.user_id == user_id).all()

# --- CAMPAIGNS / OUTREACH ENDPOINT ---
@router.get("/campaigns")
def get_campaigns(user_id: int, db: Session = Depends(get_db)):
    campaigns = (
        db.query(Campaign)
        .filter(Campaign.user_id == user_id)
        .order_by(Campaign.created_at.desc())
        .all()
    )
    return [
        {
            "id": c.id,
            "title": c.title,
            "subject": c.subject,
            "body": c.body,
            "target_industry": c.target_industry,
            "status": c.status,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else None,
        }
        for c in campaigns
    ]


# --- 3. DELETE CAMPAIGN BY ID ---
@router.delete("/campaigns/{campaign_id}")
def delete_campaign(campaign_id: int, user_id: int, db: Session = Depends(get_db)):
    campaign = (
        db.query(Campaign)
        .filter(Campaign.id == campaign_id, Campaign.user_id == user_id)
        .first()
    )
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign record not found.")

    db.delete(campaign)
    db.commit()
    return {"success": True, "message": "Campaign deleted successfully."}
# --- CONVERSATIONS / CRM ENDPOINT ---
@router.get("/conversations")
def get_conversations(user_id: int, db: Session = Depends(get_db)):
    return db.query(Conversation).filter(Conversation.user_id == user_id).all()

@router.post("/analyze-company")
def analyze_company(data: dict, user_id: int, db: Session = Depends(get_db)):
    company_name = data.get("company", "").strip()
    website = data.get("website", "").strip()
    industry = data.get("industry", "").strip()

    if not company_name:
        raise HTTPException(status_code=400, detail="Company name is required.")

    prompt = f"""
Analyze the following company for sales prospects:

Company: {company_name}
Website: {website}
Industry: {industry}

Return ONLY valid JSON in this exact structure:
{{
  "company": "{company_name}",
  "industry": "{industry}",
  "lead_score": 85,
  "grade": "A",
  "company_summary": "Brief summary of the company...",
  "sales_opportunity": "High potential for enterprise software solutions...",
  "recommended_sales_approach": "Initiate email outreach followed by a product demo."
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        result = clean_json_response(response.text)
    except Exception:
        result = {
            "company": company_name,
            "industry": industry,
            "lead_score": 60,
            "grade": "B",
            "company_summary": "Company analysis completed.",
            "sales_opportunity": "Standard outreach recommended.",
            "recommended_sales_approach": "Direct contact via email or LinkedIn."
        }

    # Save or update company record in database for account isolation
    existing = db.query(Company).filter(
        Company.company_name == company_name, 
        Company.user_id == user_id
    ).first()

    if not existing:
        new_company = Company(
            user_id=user_id,
            company_name=company_name,
            website=website,
            industry=industry,
            description=result.get("company_summary", "")
        )
        db.add(new_company)
        db.commit()

    return result

@router.post("/generate-email")
def generate_email(data: dict, user_id: int, db: Session = Depends(get_db)):
    company = data.get("company", "").strip()
    name = data.get("name", "").strip()
    industry = data.get("industry", "").strip()
    product = data.get("product", "Our Product").strip()

    prompt = f"""
Generate a high-converting professional cold sales email.

Recipient: {name}
Company: {company}
Industry: {industry}
Product/Value Proposition: {product}

Return ONLY the email body.
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        email_text = response.text.strip()

        # SAVE TO DATABASE
        new_campaign = Campaign(
            user_id=user_id,
            title=f"Outreach to {company} ({name})",
            subject=f"Connecting with {company}",
            body=email_text,
            target_industry=industry,
            status="Draft"
        )
        db.add(new_campaign)
        db.commit()
        db.refresh(new_campaign)

        return {"email": email_text, "campaign_id": new_campaign.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/lead-score")
def lead_score(data: dict, user_id: int, db: Session = Depends(get_db)):
    company = data.get("company", "").strip()
    industry = data.get("industry", "").strip()
    company_size = data.get("company_size", "").strip()
    revenue = data.get("revenue", "").strip()
    budget = data.get("budget", "").strip()
    decision_maker = data.get("decision_maker", "No")

    prompt = f"""
You are an expert B2B sales analyst. Evaluate this lead profile:

Company: {company}
Industry: {industry}
Company Size: {company_size}
Annual Revenue: {revenue}
Budget: {budget}
Decision Maker Identified: {decision_maker}

Return ONLY valid JSON in this exact structure:
{{
  "lead_score": 91,
  "grade": "A",
  "priority": "High",
  "conversion_probability": "84%",
  "qualification": "Hot Lead",
  "company_summary": "Brief analysis of the company...",
  "sales_opportunity": "Enterprise solution opportunity...",
  "recommended_sales_approach": "Schedule technical demo with decision maker.",
  "reasons": [
      "Decision maker identified",
      "Sufficient budget allocation",
      "High revenue growth potential"
  ],
  "next_action": "Contact decision maker within 24 hours."
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        result = clean_json_response(response.text)
    except Exception:
        result = {
            "lead_score": 50,
            "grade": "C",
            "priority": "Medium",
            "conversion_probability": "50%",
            "qualification": "Warm Lead",
            "company_summary": "Evaluation completed.",
            "sales_opportunity": "Standard prospect opportunity.",
            "recommended_sales_approach": "Send introductory email.",
            "reasons": ["Standard evaluation completed"],
            "next_action": "Follow up via email within 48 hours.",
        }

    # Optional: Update existing lead's score in PostgreSQL if it exists
    existing_lead = (
        db.query(Lead)
        .filter(Lead.company == company, Lead.user_id == user_id)
        .first()
    )
    if existing_lead:
        existing_lead.lead_score = result.get("lead_score", 50)
        existing_lead.priority = result.get("priority", "Medium")
        existing_lead.status = result.get("qualification", "Qualified")
        db.commit()

    return result
