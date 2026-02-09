from typing import Any, Dict, List
from urllib.parse import urlparse


def build_evidence_from_news(news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    evidence = []
    for item in news_items:
        url = item.get("url")
        domain = _extract_domain(url)
        quality = _classify_quality(domain, "news")
        evidence.append(
            {
                "title": item.get("title"),
                "url": url,
                "summary": item.get("description"),
                "age": item.get("age"),
                "source": "Brave Search",
                "signal_type": "news",
                "domain": domain,
                "quality": quality,
                "severity": item.get("severity"),
                "keyword_hits": item.get("keyword_hits"),
                "relevance_score": item.get("relevance_score"),
            }
        )
    return evidence


def build_evidence_from_trade_signals(trade_signals: Dict[str, Any]) -> List[Dict[str, Any]]:
    evidence = []
    for code, payload in trade_signals.items():
        evidence.append(
            {
                "title": payload.get("label"),
                "url": "",
                "summary": payload.get("value"),
                "age": "latest",
                "source": "World Bank",
                "signal_type": f"trade:{code}",
                "domain": "api.worldbank.org",
                "quality": "official",
            }
        )
    return evidence


def build_evidence_from_policy_signals(policy_signals: Dict[str, Any]) -> List[Dict[str, Any]]:
    evidence = []
    for code, payload in policy_signals.items():
        evidence.append(
            {
                "title": payload.get("label"),
                "url": "",
                "summary": payload.get("value"),
                "age": "latest",
                "source": "World Bank",
                "signal_type": f"policy:{code}",
                "domain": "api.worldbank.org",
                "quality": "official",
            }
        )
    return evidence


def build_evidence_from_tenders(tenders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    evidence = []
    for item in tenders:
        url = item.get("url")
        domain = _extract_domain(url)
        evidence.append(
            {
                "title": item.get("title"),
                "url": url,
                "summary": item.get("summary"),
                "age": item.get("date"),
                "source": "Tender Feed",
                "signal_type": "tender",
                "domain": domain,
                "quality": _classify_quality(domain, "tender"),
                "severity": item.get("severity"),
                "keyword_hits": item.get("keyword_hits"),
                "relevance_score": item.get("relevance_score"),
            }
        )
    return evidence


def dedupe_evidence(evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    deduped = []
    for item in evidence:
        url = item.get("url") or ""
        title = (item.get("title") or "").strip().lower()
        summary = (item.get("summary") or "").strip().lower()
        domain = ""
        if url:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
        key = (domain, title, summary[:120])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _extract_domain(url: str | None) -> str:
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return ""


def _classify_quality(domain: str, signal_type: str) -> str:
    if signal_type in {"tender"}:
        return "official"
    if signal_type.startswith("trade") or signal_type.startswith("policy"):
        return "official"
    if domain.endswith(".gov") or ".gov." in domain:
        return "official"
    if domain.endswith(".int") or domain.endswith(".edu") or domain.endswith(".ac"):
        return "official"
    if domain:
        return "media"
    return "unknown"
