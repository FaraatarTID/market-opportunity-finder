import google.generativeai as genai
import os
import json
import logging


logger = logging.getLogger(__name__)

class GeminiConfigurationError(Exception):
    pass

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables.")
            raise GeminiConfigurationError("GEMINI_API_KEY not configured.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def generate_search_query(self, country_name: str) -> str:
        prompt = f"""
        Generate a search query to find news about "tire recycling projects" and "trade with Iran" in {country_name}.
        The query should include terms in the primary local language of {country_name} AND in English.
        Return ONLY the query string, nothing else. Do not use quotes around the output.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating search query: {e}")
            return f"tire recycling news {country_name} Iran export"

    def analyze_market(self, country_name: str, data: dict) -> dict:
        """
        Analyzes market potential using Gemini.
        """
        prompt = f"""
        Analyze the tire recycling market opportunity in {country_name}.
        
        Context:
        - The user is an Iranian company looking to export tire recycling products (or set up projects) to {country_name}.
        - Analysis MUST consider this export relationship from Iran.
        
        Data provided:
        - GDP: {data.get('gdp')}
        - Population: {data.get('population')}
        - Estimated Tire Waste: {data.get('tire_waste')}
        
        Recent News Headlines (for context):
        {json.dumps(data.get('news', []), indent=2)}
        
        Please provide a JSON response with the following fields:
        - score (0-100): Overall market attractiveness score.
        - reasoning: A brief explanation of the score, incorporating the news and export context.
        - risks: List of potential risks (political, economic, sanctions, etc.).
        - opportunities: List of specific opportunities.
        - regulations: Summary of relevant environmental regulations.
        - news_analysis: A detailed analysis of the provided news headlines and how they impact the opportunity. 
          Format this as numbered points (1. 2. 3.) with bold headers using **Header:** followed by explanation.
          Each numbered point should start on a new line. Use this format:
          "1. **Key Point Title:** Explanation text here. 2. **Another Point:** More explanation."
        - news_references: List of objects with "title" and "url" for each news source mentioned in the analysis.
          Extract these from the news headlines provided above.
        
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
                "regulations": "Unknown",
                "news_analysis": "Analysis failed.",
                "news_references": []
            }

    def translate_to_persian(self, analysis: dict, country_name: str) -> dict:
        """
        Translates the analysis results to Persian for Iranian users.
        """
        prompt = f"""
        Translate the following market analysis to Persian (Farsi).
        Maintain the JSON structure but translate all text content to Persian.
        Keep the score as a number.
        
        Original analysis:
        {json.dumps(analysis, ensure_ascii=False, indent=2)}
        
        Country: {country_name}
        
        Return the translated JSON with these fields in Persian:
        - score: (keep as number)
        - reasoning: (translate to Persian)
        - risks: (translate list items to Persian)
        - opportunities: (translate list items to Persian)
        - regulations: (translate to Persian)
        - news_analysis: (translate to Persian)
        - news_references: (keep title and url, but you can translate titles to Persian if helpful)
        
        Ensure the response is valid JSON with proper Persian text encoding.
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
                
            return json.loads(text)
        except Exception as e:
            logger.error(f"Error translating to Persian: {e}")
            return analysis  # Return original if translation fails
