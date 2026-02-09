from typing import Any, Dict

import pycountry

from models.subject import Subject
from models.scoring_config import ScoringConfig
from services.data_collector import DataCollector
from services.evidence import (
    build_evidence_from_news,
    build_evidence_from_trade_signals,
    build_evidence_from_policy_signals,
    build_evidence_from_tenders,
    dedupe_evidence,
)
from services.query_builder import build_queries
from services.scoring import score_subject
from services.trade_signals import get_trade_signals
from services.policy_signals import get_policy_signals
from services.tender_sources import collect_tenders


class SubjectResolutionError(Exception):
    pass


def _resolve_country(target_name: str) -> Dict[str, str]:
    try:
        country = pycountry.countries.search_fuzzy(target_name)[0]
        return {"country_code": country.alpha_2, "country_name": country.name}
    except LookupError as exc:
        raise SubjectResolutionError(f"Country '{target_name}' not found.") from exc


def analyze_subject(subject: Subject, scoring_config: ScoringConfig | dict | None = None) -> Dict[str, Any]:
    collector = DataCollector()
    resolved = {}
    macro = {}
    trade_signals = {}
    policy_signals = {}
    warnings = []
    if isinstance(scoring_config, dict):
        scoring_config = ScoringConfig(**scoring_config)
    scoring_config = scoring_config or ScoringConfig()

    if subject.target_type == "country":
        resolved = _resolve_country(subject.target_name)
        macro = collector.get_country_data(resolved["country_code"])
        trade_signals = get_trade_signals(resolved["country_code"], collector)
        policy_signals = get_policy_signals(resolved["country_code"], collector)
    else:
        warnings.append(
            "Only country targets are fully supported in this version. Other target types "
            "return limited evidence and neutral scores."
        )

    queries = build_queries(subject)
    news = collector.get_regional_news(resolved.get("country_name", subject.target_name), queries=queries)
    tenders = collect_tenders(subject.tender_feeds)
    tender_keywords = _build_tender_keywords(subject)
    news = _classify_news(news, tender_keywords)
    filtered_tenders = _filter_tenders(tenders, tender_keywords)
    classified_tenders = _classify_tenders(filtered_tenders, tender_keywords)
    evidence = (
        build_evidence_from_news(news)
        + build_evidence_from_trade_signals(trade_signals)
        + build_evidence_from_policy_signals(policy_signals)
        + build_evidence_from_tenders(classified_tenders)
    )
    evidence = dedupe_evidence(evidence)

    scores = score_subject(subject, macro, evidence, trade_signals, scoring_config)

    return {
        "subject": subject.model_dump(),
        "resolved": resolved,
        "macro": macro,
        "trade_signals": trade_signals,
        "policy_signals": policy_signals,
        "scores": scores,
        "scoring_config": scoring_config.model_dump(),
        "evidence": evidence,
        "query_plan": queries,
        "tender_filters": tender_keywords,
        "warnings": warnings,
        "data_sources": [
            "World Bank API (macro data)",
            "World Bank API (trade indicators)",
            "World Bank API (policy indicators)",
            "Brave Search API (news discovery)",
            "Configured tender RSS/JSON feeds",
        ],
    }


def _build_tender_keywords(subject: Subject) -> list[str]:
    keywords = []
    keywords.extend(subject.products or [])
    keywords.extend(subject.signals_of_interest or [])
    keywords.extend(subject.hs_codes or [])
    return [value.strip().lower() for value in keywords if value and value.strip()]


def _filter_tenders(tenders: list[dict], keywords: list[str]) -> list[dict]:
    if not keywords:
        return tenders
    filtered = []
    for item in tenders:
        haystack = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        if any(keyword in haystack for keyword in keywords):
            filtered.append(item)
    return filtered


def _classify_tenders(tenders: list[dict], keywords: list[str]) -> list[dict]:
    classified = []
    for item in tenders:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        hits = 0
        for keyword in keywords:
            if keyword in text:
                hits += 1
        if hits >= 3:
            severity = "high"
        elif hits == 2:
            severity = "medium"
        elif hits == 1:
            severity = "low"
        else:
            severity = "none"
        new_item = dict(item)
        new_item["severity"] = severity
        new_item["keyword_hits"] = hits
        new_item["relevance_score"] = min(100, hits * 20)
        classified.append(new_item)
    return classified


def _classify_news(news: list[dict], keywords: list[str]) -> list[dict]:
    classified = []
    for item in news:
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()
        hits = 0
        for keyword in keywords:
            if keyword in text:
                hits += 1
        if hits >= 3:
            severity = "high"
        elif hits == 2:
            severity = "medium"
        elif hits == 1:
            severity = "low"
        else:
            severity = "none"
        new_item = dict(item)
        new_item["severity"] = severity
        new_item["keyword_hits"] = hits
        new_item["relevance_score"] = min(100, hits * 20)
        classified.append(new_item)
    return classified
