
from unittest import result

from sqlalchemy import text
from database.ai import model
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import Lead
from sqlalchemy import func
import json

router = APIRouter()


@router.get("/")
def home():
    return {"message": "SalesGenie API Running"}


@router.get("/dashboard")
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

@router.post("/login")
def login(data: dict):
    return {
        "success": True,
        "message": "Login successful",
        "user": data.get("email")
    }


@router.post("/signup")
def signup(data: dict):
    return {
        "success": True,
        "message": "Account created"
    }


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

    return [
        {
            "id": l.id,
            "name": l.name,
            "email": l.email,
            "phone": l.phone,
            "company": l.company,
            "industry": l.industry,
            "status": l.status,
            "created_at": l.created_at
        }
        for l in leads
    ]

@router.post("/analyze-company")
def analyze_company(data: dict):

    prompt = f"""
Analyze the following company.

Company: {data.get("company")}
Website: {data.get("website")}
Industry: {data.get("industry")}

Return ONLY valid JSON.
Do not include markdown, explanations, or extra text.

{{
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



@router.post("/lead-score")
def lead_score(data: dict):

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