from services.data_collector import DataCollector
from services.gemini_service import GeminiService
import logging

logger = logging.getLogger(__name__)

class ScoringEngine:
    def __init__(self):
        self.data_collector = DataCollector()
        self.gemini_service = GeminiService()

    def score_country(self, country_code: str, country_name: str):
        # 1. Collect Data
        data = self.data_collector.get_country_data(country_code)
        tire_waste = self.data_collector.get_tire_waste_estimate(data.get("population"))
        data["tire_waste"] = tire_waste
        
        # 2. Analyze with Gemini
        analysis = self.gemini_service.analyze_market(country_name, data)
        
        # 3. Combine results
        result = {
            "country": country_name,
            "country_code": country_code,
            "data": data,
            "analysis": analysis
        }
        return result
