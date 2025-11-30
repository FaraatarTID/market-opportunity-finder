from services.data_collector import DataCollector
from services.gemini_service import GeminiService, GeminiConfigurationError
import logging

logger = logging.getLogger(__name__)

class ScoringEngine:
    def __init__(self):
        self.data_collector = DataCollector()
        try:
            self.gemini_service = GeminiService()
        except GeminiConfigurationError as e:
            logger.error(str(e))
            self.gemini_service = None

    def score_country(self, country_code: str, country_name: str):
        # 1. Collect Data
        data = self.data_collector.get_country_data(country_code)
        # 1. Collect Data
        data = self.data_collector.get_country_data(country_code)
        
        # Collect News
        news = self.data_collector.get_regional_news(country_name)
        data["news"] = news
        
        if not self.gemini_service:
            raise GeminiConfigurationError("Gemini service not configured.")
        # 2. Analyze with Gemini
        analysis = self.gemini_service.analyze_market(country_name, data)
        
        # 3. Translate to Persian for Iranian users
        analysis_persian = self.gemini_service.translate_to_persian(analysis, country_name)
        
        # 4. Combine results
        result = {
            "country": country_name,
            "country_code": country_code,
            "data": data,
            "analysis": analysis,
            "analysis_persian": analysis_persian
        }
        return result
