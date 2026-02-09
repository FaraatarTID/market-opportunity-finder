from services.hs_utils import suggest_hs_codes


def test_suggest_hs_codes_matches_category():
    codes = suggest_hs_codes("We sell crumb rubber and rubber tiles")
    assert "4004" in codes or "4016" in codes
