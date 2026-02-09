import logging
from typing import Any, Dict, Optional

from services.data_collector import DataCollector

logger = logging.getLogger(__name__)

POLICY_INDICATORS = {
    "TM.TAX.MRCH.WM.AR.ZS": "Tariff rate, applied, weighted mean, all products (%)",
    "LP.LPI.OVRL.XQ": "Logistics performance index (overall)",
}


def _extract_latest_value(series: Any) -> Optional[float]:
    if not isinstance(series, list) or len(series) < 2:
        return None
    rows = series[1] or []
    if not rows:
        return None
    value = rows[0].get("value")
    return value


def get_policy_signals(country_code: str, collector: DataCollector) -> Dict[str, Any]:
    signals = {}
    for code, label in POLICY_INDICATORS.items():
        try:
            series = collector.get_indicator_series(country_code, code)
            value = _extract_latest_value(series)
            signals[code] = {"label": label, "value": value}
        except Exception as exc:
            logger.error("Policy indicator fetch failed for %s: %s", code, exc)
            signals[code] = {"label": label, "value": None}
    return signals
