from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Subject(BaseModel):
    target_type: Literal["country", "sector", "product", "company", "supply_chain"] = "country"
    target_name: str = Field(..., min_length=2)
    region: Optional[str] = None
    products: List[str] = Field(default_factory=list)
    signals_of_interest: List[str] = Field(default_factory=list)
    risk_focus: List[str] = Field(default_factory=list)
    time_horizon_months: int = Field(default=12, ge=1, le=60)
    languages: List[str] = Field(default_factory=lambda: ["en"])
    hs_codes: List[str] = Field(default_factory=list)
    tender_feeds: List[str] = Field(default_factory=list)
