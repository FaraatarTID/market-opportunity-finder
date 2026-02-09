from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class CompetitiveLandscape(BaseModel):
    market_saturation: Optional[str] = None
    key_players: List[str] = []
    competitive_advantage: Optional[str] = None
    market_gaps: Optional[str] = None


class MarketEntryStrategy(BaseModel):
    recommended_approach: Optional[str] = None
    rationale: Optional[str] = None
    key_partners: List[str] = []
    entry_barriers: List[str] = []
    timeline: Optional[str] = None


class FinancialProjections(BaseModel):
    estimated_market_size_usd: Optional[float] = None
    potential_market_share: Optional[str] = None
    estimated_revenue_year1: Optional[float] = None
    estimated_revenue_year3: Optional[float] = None
    initial_investment_required: Optional[float] = None
    roi_timeline: Optional[str] = None
    key_assumptions: List[str] = []


class SanctionsImpact(BaseModel):
    severity: Optional[str] = None
    specific_restrictions: List[str] = []
    workarounds: List[str] = []


class AnalysisModel(BaseModel):
    score: Optional[float] = None
    dimensional_scores: Dict[str, Any] = {}
    reasoning: Optional[str] = None
    competitive_landscape: CompetitiveLandscape = CompetitiveLandscape()
    market_entry_strategy: MarketEntryStrategy = MarketEntryStrategy()
    financial_projections: FinancialProjections = FinancialProjections()
    opportunities: List[str] = []
    risks: List[str] = []
    risk_mitigation_strategies: List[Dict[str, Any]] = []
    critical_success_factors: List[str] = []
    implementation_roadmap: List[Dict[str, Any]] = []
    news_analysis: Optional[str] = None
    news_references: List[Dict[str, Any]] = []
    regulations: Optional[str] = None
    sanctions_impact: SanctionsImpact = SanctionsImpact()
    executive_summary: Optional[str] = None
