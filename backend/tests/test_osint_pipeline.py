from models.subject import Subject
import services.osint_pipeline as pipeline


class DummyCollector:
    def get_country_data(self, _code):
        return {"gdp": 1_000_000_000, "population": 1_000_000, "lat": 0, "lng": 0}

    def get_regional_news(self, _name, queries=None):
        return [{"title": "News", "url": "https://example.com", "description": "rubber import"}]


def test_analyze_subject_outputs_expected_keys(monkeypatch):
    monkeypatch.setattr(pipeline, "DataCollector", lambda: DummyCollector())
    monkeypatch.setattr(pipeline, "get_trade_signals", lambda _code, _collector: {"NE.IMP.GNFS.CD": {"label": "Imports", "value": 1}})
    monkeypatch.setattr(pipeline, "get_policy_signals", lambda _code, _collector: {"TM.TAX.MRCH.WM.AR.ZS": {"label": "Tariff", "value": 5}})
    monkeypatch.setattr(pipeline, "collect_tenders", lambda _feeds: [{"title": "Tender", "url": "https://tenders.gov", "summary": "rubber tiles"}])
    monkeypatch.setattr(pipeline, "_resolve_country", lambda _name: {"country_code": "TR", "country_name": "Turkey"})

    subject = Subject(target_name="Turkey", products=["rubber"])
    result = pipeline.analyze_subject(subject)
    assert "scores" in result
    assert "evidence" in result
    assert len(result["evidence"]) > 0
