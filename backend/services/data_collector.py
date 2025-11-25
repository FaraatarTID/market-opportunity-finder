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
        
        for indicator in indicators:
            try:
                url = f"{self.wb_base_url}/country/{country_code}/indicator/{indicator}?format=json&per_page=1"
                response = requests.get(url)
                response.raise_for_status()
                result = response.json()
                
                if len(result) > 1 and result[1]:
                    value = result[1][0].get("value")
                    data[indicator] = value
                else:
                    data[indicator] = None
            except Exception as e:
                logger.error(f"Error fetching data for {country_code} - {indicator}: {e}")
                data[indicator] = None
                
        return {
            "gdp": data.get("NY.GDP.MKTP.CD"),
            "population": data.get("SP.POP.TOTL")
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
