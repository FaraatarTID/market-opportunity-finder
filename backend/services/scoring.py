import math
from typing import Any, Dict, List

from models.subject import Subject
from models.scoring_config import ScoringConfig


def _log_score(value: float, min_log: float, max_log: float) -> int:
    if value <= 0:
        return 0
    score = (math.log10(value) - min_log) / (max_log - min_log)
    return max(0, min(100, int(score * 100)))


def score_subject(
    subject: Subject,
    macro: Dict[str, Any],
    evidence: List[Dict[str, Any]],
    trade_signals: Dict[str, Any],
    config: ScoringConfig,
) -> Dict[str, Any]:
    if not isinstance(config, ScoringConfig):
        config = ScoringConfig(**config)
    gdp = macro.get("gdp") or 0
    population = macro.get("population") or 0

    market_demand = int(
        0.6 * _log_score(gdp, min_log=9, max_log=14)
        + 0.4 * _log_score(population, min_log=6, max_log=10)
    )

    signal_count = len(evidence)
    signal_score = min(100, signal_count * 5)

    import_value = trade_signals.get("NE.IMP.GNFS.CD", {}).get("value") or 0
    trade_ease = int(0.5 * _log_score(import_value, min_log=9, max_log=13) + 0.5 * 50)
    political_risk = 50
    financial_viability = int(0.5 * market_demand + 0.5 * signal_score)
    strategic_fit = 50

    weights = config.normalized_weights()
    overall = int(
        weights.get("market_demand", 0) * market_demand
        + weights.get("trade_ease", 0) * trade_ease
        + weights.get("political_risk", 0) * political_risk
        + weights.get("financial_viability", 0) * financial_viability
        + weights.get("strategic_fit", 0) * strategic_fit
    )

    rationale = (
        "Score is based on macro demand signals (GDP/population) and the volume of recent "
        "open-source evidence. Trade ease incorporates import volume. Political risk and "
        "strategic fit are neutral defaults until more data sources are integrated."
    )

    confidence = _calculate_confidence(macro, trade_signals, evidence)
    confidence_breakdown = _confidence_breakdown(macro, trade_signals, evidence)
    confidence_sources = _confidence_sources(evidence)

    return {
        "overall_score": overall,
        "confidence": confidence,
        "confidence_breakdown": confidence_breakdown,
        "confidence_sources": confidence_sources,
        "dimensional_scores": {
            "market_demand": market_demand,
            "signal_strength": signal_score,
            "trade_ease": trade_ease,
            "political_risk": political_risk,
            "financial_viability": financial_viability,
            "strategic_fit": strategic_fit,
        },
        "rationale": rationale,
        "weights": weights,
    }


def _calculate_confidence(
    macro: Dict[str, Any],
    trade_signals: Dict[str, Any],
    evidence: List[Dict[str, Any]],
) -> int:
    score = 0
    if macro.get("gdp"):
        score += 25
    if macro.get("population"):
        score += 25
    if trade_signals.get("NE.IMP.GNFS.CD", {}).get("value"):
        score += 20
    if trade_signals.get("TM.VAL.MRCH.CD.WT", {}).get("value"):
        score += 10
    if len(evidence) >= 5:
        score += 20
    elif len(evidence) >= 1:
        score += 10
    source_types = _confidence_sources(evidence)
    if source_types.get("news", 0) >= 5:
        score += 10
    if source_types.get("trade", 0) >= 2:
        score += 5
    if source_types.get("official", 0) >= 3:
        score += 10
    return min(100, score)


def _confidence_breakdown(
    macro: Dict[str, Any],
    trade_signals: Dict[str, Any],
    evidence: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "has_gdp": bool(macro.get("gdp")),
        "has_population": bool(macro.get("population")),
        "has_imports_goods_services": bool(trade_signals.get("NE.IMP.GNFS.CD", {}).get("value")),
        "has_merch_imports": bool(trade_signals.get("TM.VAL.MRCH.CD.WT", {}).get("value")),
        "evidence_count": len(evidence),
    }


def _confidence_sources(evidence: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {"news": 0, "trade": 0, "policy": 0, "tender": 0, "official": 0, "other": 0}
    for item in evidence:
        signal_type = (item.get("signal_type") or "").lower()
        quality = (item.get("quality") or "").lower()
        if signal_type.startswith("trade:"):
            counts["trade"] += 1
        elif signal_type.startswith("policy:"):
            counts["policy"] += 1
        elif signal_type == "news":
            counts["news"] += 1
        elif signal_type == "tender":
            counts["tender"] += 1
        else:
            counts["other"] += 1
        if quality == "official":
            counts["official"] += 1
    return counts
