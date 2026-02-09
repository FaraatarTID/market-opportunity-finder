from typing import Dict

from pydantic import BaseModel, Field


class ScoringConfig(BaseModel):
    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "market_demand": 0.35,
            "trade_ease": 0.2,
            "political_risk": 0.2,
            "financial_viability": 0.15,
            "strategic_fit": 0.1,
        }
    )

    def normalized_weights(self) -> Dict[str, float]:
        total = sum(self.weights.values()) or 1.0
        return {key: value / total for key, value in self.weights.items()}
