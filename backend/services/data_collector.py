import logging
import os
from typing import List, Optional

logger = logging.getLogger(__name__)

from services.cache import SimpleFileCache
from services.http_client import HttpClient


class DataCollector:
    def __init__(self):
        self.wb_base_url = "https://api.worldbank.org/v2"
        self.http = HttpClient(timeout_seconds=10)
        cache_path = os.path.join(os.path.dirname(__file__), "..", ".cache", "osint_cache.json")
        self.cache = SimpleFileCache(os.path.normpath(cache_path), default_ttl_seconds=86400)

    def get_country_data(self, country_code: str):
        """
        Fetches basic economic data for a country from World Bank API.
        Indicators:
        - NY.GDP.MKTP.CD: GDP (current US$)
        - SP.POP.TOTL: Population, total
        """
        indicators = ["NY.GDP.MKTP.CD", "SP.POP.TOTL"]
        data = {}
        
        # Fetch basic country info for lat/lng
        try:
            info_url = f"{self.wb_base_url}/country/{country_code}?format=json"
            cached = self.cache.get(f"wb:country:{country_code}")
            if cached:
                info_res = cached
            else:
                info_res = self.http.get_json(info_url)
                self.cache.set(f"wb:country:{country_code}", info_res, ttl_seconds=86400)
            if len(info_res) > 1 and info_res[1]:
                country_info = info_res[1][0]
                data["lat"] = float(country_info.get("latitude", 0))
                data["lng"] = float(country_info.get("longitude", 0))
            else:
                data["lat"] = 0.0
                data["lng"] = 0.0
        except Exception as e:
            logger.error(f"Error fetching country info for {country_code}: {e}")
            data["lat"] = 0.0
            data["lng"] = 0.0

        for indicator in indicators:
            try:
                result = self.get_indicator_series(country_code, indicator)
                
                if len(result) > 1 and result[1]:
                    # For GDP and Population, the value is in result[1][0]['value']
                    # For lat/lng, we need to check the country info in the response
                    # The World Bank API response structure for indicators includes country info in each item
                    # But it's better to fetch lat/lng from a separate endpoint or parse it from the indicator response if available
                    # Actually, the indicator response contains 'country': {'id': 'BR', 'value': 'Brazil'} but not lat/lng directly in the indicator value
                    # However, we can fetch country info specifically.
                    
                    value = result[1][0].get("value")
                    data[indicator] = value
                    
                    # Try to extract lat/lng from the first valid response if not already set
                    if "lat" not in data and result[1][0].get("countryiso3code"):
                         # We can't easily get lat/lng from the indicator response directly as it's not standard
                         # Let's make a separate call for country info which is cleaner
                         pass
                else:
                    data[indicator] = None
            except Exception as e:
                logger.error(f"Error fetching data for {country_code} - {indicator}: {e}")
                data[indicator] = None
                
        return {
            "gdp": data.get("NY.GDP.MKTP.CD"),
            "population": data.get("SP.POP.TOTL"),
            "lat": data.get("lat"),
            "lng": data.get("lng")
        }

    def get_indicator_series(self, country_code: str, indicator: str):
        url = f"{self.wb_base_url}/country/{country_code}/indicator/{indicator}?format=json&per_page=1"
        cache_key = f"wb:indicator:{country_code}:{indicator}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        result = self.http.get_json(url)
        self.cache.set(cache_key, result, ttl_seconds=86400)
        return result

    def get_regional_news(self, country_name: str, queries: Optional[List[str]] = None):
        """
        Fetches comprehensive news about tire recycling products demand, trade, and Iran relations
        in the specified country using Brave Search API.
        """
        api_key = os.getenv("BRAVE_API_KEY")
        if not api_key:
            logger.warning("BRAVE_API_KEY not found. Skipping news search.")
            return []

        # Multiple search queries for comprehensive coverage of EXPORT potential
        if not queries:
            queries = [
                f"import of rubber products {country_name} from Iran",
                f"demand for crumb rubber {country_name} construction",
                f"automotive industry trends {country_name} rubber parts",
                f"infrastructure projects {country_name} asphalt rubber",
                f"{country_name} Iran trade agreement industrial goods",
            ]
        
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "X-Subscription-Token": api_key,
            "Accept": "application/json"
        }
        
        all_results = []
        seen_urls = set()  # Avoid duplicates
        
        for query in queries:
            params = {
                "q": query,
                "count": 5,
                "freshness": "py"  # Past year
            }

            try:
                cache_key = f"brave:{query}"
                cached = self.cache.get(cache_key)
                if cached:
                    data = cached
                else:
                    data = self.http.get_json(url, headers=headers, params=params)
                    self.cache.set(cache_key, data, ttl_seconds=3600)
                
                if "web" in data and "results" in data["web"]:
                    for item in data["web"]["results"]:
                        url_link = item.get("url")
                        # Avoid duplicates
                        if url_link not in seen_urls:
                            seen_urls.add(url_link)
                            all_results.append({
                                "title": item.get("title"),
                                "url": url_link,
                                "description": item.get("description"),
                                "age": item.get("age")
                            })
            except Exception as e:
                logger.error(f"Error fetching news for query '{query}': {e}")
                continue
        
        # Return top 15 most relevant results
        return all_results[:15]
