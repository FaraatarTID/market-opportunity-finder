from services.evidence import dedupe_evidence, build_evidence_from_news


def test_dedupe_evidence_removes_duplicates():
    evidence = [
        {"title": "A", "url": "https://example.com/a", "summary": "X", "signal_type": "news"},
        {"title": "A", "url": "https://example.com/a", "summary": "X", "signal_type": "news"},
    ]
    deduped = dedupe_evidence(evidence)
    assert len(deduped) == 1


def test_build_evidence_from_news_sets_quality():
    news_items = [{"title": "Gov report", "url": "https://example.gov/report", "description": "x"}]
    evidence = build_evidence_from_news(news_items)
    assert evidence[0]["quality"] == "official"
