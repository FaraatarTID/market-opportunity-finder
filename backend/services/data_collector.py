import requests
import logging

logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        self.wb_base_url = "http://api.worldbank.org/v2"

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
            resp = requests.get(info_url)
            resp.raise_for_status()
            info_res = resp.json()
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
                url = f"{self.wb_base_url}/country/{country_code}/indicator/{indicator}?format=json&per_page=1"
                response = requests.get(url)
                response.raise_for_status()
                result = response.json()
                
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

    def get_tire_waste_estimate(self, population: int):
        """
        Estimates tire waste based on population.
        Rough estimate: 1 tire per person per year in developed, 0.2 in developing.
        We'll use a conservative 0.3 for now as a baseline for developing nations.
        """
        if not population:
            return 0
        return int(population * 0.3)
