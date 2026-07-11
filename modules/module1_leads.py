from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Lead
from database.schemas import LeadCreate, LeadUpdate

router = APIRouter()


@router.post("/leads")
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    try:
        new_lead = Lead(
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            company=lead.company,
            industry=lead.industry,
        )

        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)

        return {
            "message": "Lead added successfully",
            "id": new_lead.id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/leads")
def get_all_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    return leads
@router.get("/leads/{lead_id}")
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")

    return lead

@router.put("/leads/{lead_id}")
def update_lead(
    lead_id: int,
    updated_lead: LeadUpdate,
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead.name = updated_lead.name
    lead.email = updated_lead.email
    lead.phone = updated_lead.phone
    lead.company = updated_lead.company
    lead.industry = updated_lead.industry
    lead.status = updated_lead.status

    db.commit()
    db.refresh(lead)

    return {
        "message": "Lead updated successfully",
        "lead": lead
    }

@router.delete("/leads/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")

    db.delete(lead)
    db.commit()

    return {
        "message": "Lead deleted successfully"
    }