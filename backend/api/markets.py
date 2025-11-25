from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.scoring_engine import ScoringEngine

router = APIRouter()
scoring_engine = ScoringEngine()

class MarketRequest(BaseModel):
    country_code: str
    country_name: str

@router.post("/analyze")
async def analyze_market(request: MarketRequest):
    try:
        result = scoring_engine.score_country(request.country_code, request.country_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
