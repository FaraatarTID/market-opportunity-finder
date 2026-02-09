from typing import List

from models.subject import Subject


def _normalize_list(values: List[str]) -> List[str]:
    return [value.strip() for value in values if value and value.strip()]


def build_queries(subject: Subject) -> List[str]:
    products = _normalize_list(subject.products) or ["recycled rubber", "crumb rubber"]
    signals = _normalize_list(subject.signals_of_interest) or [
        "import demand",
        "construction projects",
        "automotive production",
        "infrastructure tenders",
    ]
    risk_focus = _normalize_list(subject.risk_focus)
    hs_codes = _normalize_list(subject.hs_codes)

    base = []
    for product in products:
        base.append(f"{product} market {subject.target_name}")
        base.append(f"{product} import {subject.target_name}")

    for signal in signals:
        base.append(f"{signal} {subject.target_name}")

    if hs_codes:
        for code in hs_codes:
            base.append(f"HS {code} {subject.target_name} import")
            base.append(f"HS code {code} {subject.target_name} tariff")

    if risk_focus:
        for risk in risk_focus:
            base.append(f"{risk} {subject.target_name}")

    # Deduplicate while preserving order
    seen = set()
    queries = []
    for query in base:
        if query not in seen:
            seen.add(query)
            queries.append(query)
    return queries[:10]
