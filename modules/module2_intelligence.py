from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.schemas import LeadScoreRequest
from services.gemini_service import score_lead


from services.gemini_service import analyze_company

router = APIRouter()


class CompanyRequest(BaseModel):
    company: str

@router.post("/analyze-company")
def company_analysis(request: CompanyRequest):
    try:
        result = analyze_company(request.company)

        return {
            "company": request.company,
            "analysis": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lead-score")
def get_lead_score(request: LeadScoreRequest):

    result = score_lead(
        request.company,
        request.industry
    )

    return {
        "company": request.company,
        "analysis": result
    }
