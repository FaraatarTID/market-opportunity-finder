import logging
from typing import Any, Dict, Optional

from services.data_collector import DataCollector

logger = logging.getLogger(__name__)

TRADE_INDICATORS = {
    "NE.IMP.GNFS.CD": "Imports of goods and services (current US$)",
    "TM.VAL.MRCH.CD.WT": "Merchandise imports (current US$)",
}


def _extract_latest_value(series: Any) -> Optional[float]:
    if not isinstance(series, list) or len(series) < 2:
        return None
    rows = series[1] or []
    if not rows:
        return None
    value = rows[0].get("value")
    return value


def get_trade_signals(country_code: str, collector: DataCollector) -> Dict[str, Any]:
    signals = {}
    for code, label in TRADE_INDICATORS.items():
        try:
            series = collector.get_indicator_series(country_code, code)
            value = _extract_latest_value(series)
            signals[code] = {"label": label, "value": value}
        except Exception as exc:
            logger.error("Trade indicator fetch failed for %s: %s", code, exc)
            signals[code] = {"label": label, "value": None}
    return signals
