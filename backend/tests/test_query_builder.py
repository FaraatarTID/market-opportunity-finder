from models.subject import Subject
from services.query_builder import build_queries


def test_build_queries_includes_products_and_hs():
    subject = Subject(
        target_name="Turkey",
        products=["crumb rubber"],
        hs_codes=["4004"],
        signals_of_interest=["import growth"],
    )
    queries = build_queries(subject)
    joined = " ".join(queries)
    assert "crumb rubber" in joined
    assert "HS 4004" in joined
    assert "import growth Turkey" in joined
