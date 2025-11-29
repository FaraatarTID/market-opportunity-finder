from exceptions import GeminiConfigurationError
from fastapi import APIRouter, HTTPException
import pycountry
from pydantic import BaseModel
from services.scoring_engine import ScoringEngine

router = APIRouter()

class MarketRequest(BaseModel):
    country_name: str

@router.post("/analyze")
async def analyze_market(request: MarketRequest):
    try:
        country = pycountry.countries.search_fuzzy(request.country_name)[0]
        country_code = country.alpha_2
        country_name = country.name
    except LookupError:
            raise HTTPException(status_code=404, detail=f"Country '{request.country_name}' not found.")
    except Exception as e:
        # If pycountry fails in another way
        raise HTTPException(status_code=500, detail=f"Error validating country: {str(e)}")

    try:
        # Initialize scoring engine inside the handler to avoid module-level initialization errors
        scoring_engine = ScoringEngine()
        result = scoring_engine.score_country(country_code, country_name)
        return result
    except GeminiConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
