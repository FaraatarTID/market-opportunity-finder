import json
import os
from typing import List


def suggest_hs_codes(product_text: str) -> List[str]:
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "hs_codes.json")
    config_path = os.path.normpath(config_path)
    if not os.path.exists(config_path):
        return []
    try:
        with open(config_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        categories = payload.get("categories", {})
        product_text = product_text.lower()
        suggestions = []
        for key, codes in categories.items():
            if key.replace("_", " ") in product_text or key in product_text:
                suggestions.extend(codes)
        return suggestions
    except Exception:
        return []
