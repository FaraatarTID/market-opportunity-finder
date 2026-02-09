import json
import logging
import os
import xml.etree.ElementTree as ET
from typing import Any, Dict, List

from services.cache import SimpleFileCache
from services.http_client import HttpClient

logger = logging.getLogger(__name__)


class TenderSource:
    def __init__(self, name: str, source_type: str, url: str):
        self.name = name
        self.source_type = source_type
        self.url = url


def _load_config_sources() -> List[TenderSource]:
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "tender_sources.json")
    config_path = os.path.normpath(config_path)
    if not os.path.exists(config_path):
        return []
    try:
        with open(config_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        sources = []
        for item in payload.get("sources", []):
            sources.append(TenderSource(item.get("name", "Unknown"), item.get("type", "rss"), item.get("url", "")))
        return sources
    except Exception as exc:
        logger.error("Failed to load tender sources config: %s", exc)
        return []


def _parse_rss(xml_text: str) -> List[Dict[str, Any]]:
    items = []
    try:
        root = ET.fromstring(xml_text)
        for item in root.findall(".//item"):
            title = item.findtext("title") or ""
            link = item.findtext("link") or ""
            description = item.findtext("description") or ""
            pub_date = item.findtext("pubDate") or ""
            items.append(
                {
                    "title": title.strip(),
                    "url": link.strip(),
                    "summary": description.strip(),
                    "date": pub_date.strip(),
                }
            )
    except Exception as exc:
        logger.error("Failed to parse RSS: %s", exc)
    return items


def _parse_json(text: str) -> List[Dict[str, Any]]:
    items = []
    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            payload = payload.get("items", [])
        if not isinstance(payload, list):
            return items
        for item in payload:
            items.append(
                {
                    "title": str(item.get("title", "")),
                    "url": str(item.get("url", "")),
                    "summary": str(item.get("summary", item.get("description", ""))),
                    "date": str(item.get("date", item.get("published", ""))),
                }
            )
    except Exception as exc:
        logger.error("Failed to parse tender JSON: %s", exc)
    return items


def collect_tenders(extra_sources: List[str] | None = None) -> List[Dict[str, Any]]:
    http = HttpClient(timeout_seconds=10)
    cache_path = os.path.join(os.path.dirname(__file__), "..", ".cache", "tender_cache.json")
    cache = SimpleFileCache(os.path.normpath(cache_path), default_ttl_seconds=3600)

    sources = _load_config_sources()
    if extra_sources:
        for url in extra_sources:
            sources.append(TenderSource("Custom", "rss", url))

    all_items = []
    for source in sources:
        if not source.url:
            continue
        cache_key = f"tender:{source.source_type}:{source.url}"
        cached = cache.get(cache_key)
        if cached:
            all_items.extend(cached)
            continue
        try:
            if source.source_type == "json":
                text = http.get_text(source.url)
                items = _parse_json(text)
            else:
                xml_text = http.get_text(source.url)
                items = _parse_rss(xml_text)
            cache.set(cache_key, items, ttl_seconds=3600)
            all_items.extend(items)
        except Exception as exc:
            logger.error("Tender source failed %s: %s", source.url, exc)
            continue

    return all_items
