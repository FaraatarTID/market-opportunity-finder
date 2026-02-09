from models.scoring_config import ScoringConfig
from services.scoring import score_subject
from models.subject import Subject


def test_scoring_weights_normalize():
    config = ScoringConfig(weights={"market_demand": 2, "trade_ease": 1, "political_risk": 1, "financial_viability": 0, "strategic_fit": 0})
    weights = config.normalized_weights()
    assert abs(sum(weights.values()) - 1.0) < 1e-6


def test_confidence_increases_with_evidence():
    subject = Subject(target_name="Turkey")
    macro = {"gdp": 1_000_000, "population": 1_000_000}
    trade = {"NE.IMP.GNFS.CD": {"value": 1_000_000_000}, "TM.VAL.MRCH.CD.WT": {"value": 1_000_000_000}}
    evidence = [{"signal_type": "news", "quality": "official"} for _ in range(5)]
    result = score_subject(subject, macro, evidence, trade, ScoringConfig())
    assert result["confidence"] >= 70
