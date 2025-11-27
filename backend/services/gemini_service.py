import google.generativeai as genai
import os
import json
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables.")
            raise GeminiConfigurationError("GEMINI_API_KEY not configured.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def analyze_market(self, country_name: str, data: dict) -> dict:
        """
        Analyzes market potential using Gemini.
        """
        prompt = f"""
        Analyze the tire recycling market opportunity in {country_name}.
        
        Data provided:
        - GDP: {data.get('gdp')}
        - Population: {data.get('population')}
        - Estimated Tire Waste: {data.get('tire_waste')}
        
        Please provide a JSON response with the following fields:
        - score (0-100): Overall market attractiveness score.
        - reasoning: A brief explanation of the score.
        - risks: List of potential risks (political, economic, etc.).
        - opportunities: List of specific opportunities.
        - regulations: Summary of relevant environmental regulations (if known, otherwise general expectations).
        
        Ensure the response is valid JSON.
        """
        
        try:
            if not self.model:
                raise Exception("Gemini API key not configured")
                
            response = self.model.generate_content(prompt)
            # Extract JSON from response (handle potential markdown formatting)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
                
            return json.loads(text)
        except Exception as e:
            logger.error(f"Error analyzing market for {country_name}: {e}")
            return {
                "score": 0,
                "reasoning": "Analysis failed.",
                "risks": [],
                "opportunities": [],
                "regulations": "Unknown"
            }
